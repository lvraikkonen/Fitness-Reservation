import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, message } from 'antd';
import { getVenues, createVenue, updateVenue, deleteVenue } from '../../services/venueService';

const VenueManagement = () => {
  const [venues, setVenues] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [editingVenue, setEditingVenue] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchVenues();
  }, []);

  const fetchVenues = async () => {
    setLoading(true);
    try {
      const data = await getVenues();
      console.log(data);
      setVenues(data); // 直接设置返回的数组
    } catch (error) {
      console.error('Error fetching venues:', error);
      message.error('Failed to fetch venues');
    } finally {
      setLoading(false);
    }
  };

  const showModal = (venue = null) => {
    setEditingVenue(venue);
    form.setFieldsValue(venue || {});
    setIsModalVisible(true);
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingVenue) {
        await updateVenue(editingVenue.id, values);
        message.success('Venue updated successfully');
      } else {
        await createVenue(values);
        message.success('Venue added successfully');
      }
      setIsModalVisible(false);
      fetchVenues();
    } catch (error) {
      console.error('Operation failed:', error);
      message.error('Operation failed');
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteVenue(id);
      message.success('Venue deleted successfully');
      fetchVenues();
    } catch (error) {
      console.error('Delete failed:', error);
      message.error('Delete failed');
    }
  };

  const columns = [
    { 
      title: 'ID', 
      dataIndex: 'id', 
      key: 'id' 
    },
    { 
      title: 'Name', 
      dataIndex: 'name', 
      key: 'name' 
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <>
          <Button onClick={() => showModal(record)} style={{ marginRight: 8 }}>Edit</Button>
          <Button onClick={() => handleDelete(record.id)} danger>Delete</Button>
        </>
      ),
    },
  ];

  return (
    <div>
      <h2>Venue Management</h2>
      <Button onClick={() => showModal()} type="primary" style={{ marginBottom: 16 }}>
        Add Venue
      </Button>
      <Table 
        columns={columns} 
        dataSource={venues} 
        rowKey="id" 
        loading={loading}
      />
      <Modal
        title={editingVenue ? 'Edit Venue' : 'Add Venue'}
        visible={isModalVisible}
        onOk={handleOk}
        onCancel={() => setIsModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input the venue name!' }]}>
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default VenueManagement;