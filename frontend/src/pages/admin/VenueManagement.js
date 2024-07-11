// src/pages/admin/VenueManagement.js
import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, message } from 'antd';
import { venueApi } from '../../services/api';

const VenueManagement = () => {
  const [venues, setVenues] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [editingVenue, setEditingVenue] = useState(null);

  useEffect(() => {
    fetchVenues();
  }, []);

  const fetchVenues = async () => {
    try {
      const response = await venueApi.get('/');
      setVenues(response.data);
    } catch (error) {
      message.error('Failed to fetch venues');
    }
  };

  const showModal = (venue = null) => {
    setEditingVenue(venue);
    if (venue) {
      form.setFieldsValue(venue);
    } else {
      form.resetFields();
    }
    setIsModalVisible(true);
  };

  const handleOk = () => {
    form.validateFields().then(async (values) => {
      try {
        if (editingVenue) {
          await venueApi.put(`/${editingVenue.id}`, values);
          message.success('Venue updated successfully');
        } else {
          await venueApi.post('/', values);
          message.success('Venue added successfully');
        }
        setIsModalVisible(false);
        fetchVenues();
      } catch (error) {
        message.error('Operation failed');
      }
    });
  };

  const handleDelete = async (id) => {
    try {
      await venueApi.delete(`/${id}`);
      message.success('Venue deleted successfully');
      fetchVenues();
    } catch (error) {
      message.error('Delete failed');
    }
  };

  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Location', dataIndex: 'location', key: 'location' },
    { title: 'Capacity', dataIndex: 'capacity', key: 'capacity' },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <>
          <Button onClick={() => showModal(record)}>Edit</Button>
          <Button onClick={() => handleDelete(record.id)} danger>
            Delete
          </Button>
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
      <Table columns={columns} dataSource={venues} rowKey="id" />
      <Modal
        title={editingVenue ? 'Edit Venue' : 'Add Venue'}
        visible={isModalVisible}
        onOk={handleOk}
        onCancel={() => setIsModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="location" label="Location" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="capacity" label="Capacity" rules={[{ required: true }]}>
            <Input type="number" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default VenueManagement;