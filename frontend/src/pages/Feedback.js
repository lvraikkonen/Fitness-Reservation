import React, { useState, useEffect } from 'react';
import { List, Card, Modal, Form, Input, Button, Rate, message, Spin, Pagination, Tabs } from 'antd';
import { EditOutlined, DeleteOutlined, CommentOutlined } from '@ant-design/icons';
import { getFeedbacks, getMyFeedbacks, createFeedback, updateFeedback, deleteFeedback, replyToFeedback } from '../services/feedbackService';
import { useAuth } from '../contexts/AuthContext';

const { TextArea } = Input;
const { TabPane } = Tabs;

const Feedback = () => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [editingFeedbackId, setEditingFeedbackId] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [activeTab, setActiveTab] = useState('all');
  const { user } = useAuth();

  useEffect(() => {
    fetchFeedbacks();
  }, [page, activeTab]);

  const fetchFeedbacks = async () => {
    setLoading(true);
    try {
      let data;
      if (activeTab === 'my') {
        data = await getMyFeedbacks(page);
      } else {
        data = await getFeedbacks(page);
      }
      setFeedbacks(data.items);
      setTotal(data.total);
    } catch (error) {
      message.error('Failed to fetch feedbacks');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingFeedbackId) {
        await updateFeedback(editingFeedbackId, values);
        message.success('Feedback updated successfully');
      } else {
        await createFeedback(values);
        message.success('Feedback submitted successfully');
      }
      setModalVisible(false);
      form.resetFields();
      fetchFeedbacks();
    } catch (error) {
      message.error('Failed to submit feedback');
    }
  };

  const handleEdit = (feedback) => {
    setEditingFeedbackId(feedback.id);
    form.setFieldsValue(feedback);
    setModalVisible(true);
  };

  const handleDelete = async (feedbackId) => {
    try {
      await deleteFeedback(feedbackId);
      message.success('Feedback deleted successfully');
      fetchFeedbacks();
    } catch (error) {
      message.error('Failed to delete feedback');
    }
  };

  const handleReply = async (feedbackId, reply) => {
    try {
      await replyToFeedback(feedbackId, reply);
      message.success('Reply submitted successfully');
      fetchFeedbacks();
    } catch (error) {
      message.error('Failed to submit reply');
    }
  };

  const renderFeedbackList = () => (
    <>
      <List
        grid={{ gutter: 16, column: 3 }}
        dataSource={feedbacks}
        renderItem={(item) => (
          <List.Item>
            <Card
              actions={[
                item.user_id === user.id && (
                  <EditOutlined key="edit" onClick={() => handleEdit(item)} />
                ),
                item.user_id === user.id && (
                  <DeleteOutlined key="delete" onClick={() => handleDelete(item.id)} />
                ),
                user.role === 'admin' && (
                  <CommentOutlined
                    key="reply"
                    onClick={() => {
                      Modal.confirm({
                        title: 'Reply to Feedback',
                        content: (
                          <TextArea rows={4} onChange={(e) => (this.replyContent = e.target.value)} />
                        ),
                        onOk: () => handleReply(item.id, this.replyContent),
                      });
                    }}
                  />
                ),
              ].filter(Boolean)}
            >
              <Card.Meta
                title={item.title}
                description={
                  <>
                    <p><strong>User:</strong> {item.user_name}</p>
                    <Rate disabled defaultValue={item.rating} />
                    <p>{item.content}</p>
                    {item.reply && (
                      <div>
                        <strong>Reply:</strong> {item.reply}
                      </div>
                    )}
                  </>
                }
              />
            </Card>
          </List.Item>
        )}
      />
      <Pagination
        current={page}
        total={total}
        onChange={(newPage) => setPage(newPage)}
        pageSize={10}
        showSizeChanger={false}
      />
    </>
  );

  return (
    <Spin spinning={loading}>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="All Feedbacks" key="all">
          <Button
            type="primary"
            onClick={() => {
              setEditingFeedbackId(null);
              form.resetFields();
              setModalVisible(true);
            }}
            style={{ marginBottom: 16 }}
          >
            Submit Feedback
          </Button>
          {renderFeedbackList()}
        </TabPane>
        <TabPane tab="My Feedbacks" key="my">
          {renderFeedbackList()}
        </TabPane>
      </Tabs>

      <Modal
        title={editingFeedbackId ? "Edit Feedback" : "Submit Feedback"}
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleSubmit} layout="vertical">
          <Form.Item name="title" label="Title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="content" label="Content" rules={[{ required: true }]}>
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item name="rating" label="Rating" rules={[{ required: true }]}>
            <Rate />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              {editingFeedbackId ? "Update" : "Submit"}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </Spin>
  );
};

export default Feedback;