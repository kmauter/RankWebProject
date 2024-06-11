import React from 'react';

import { Form } from 'react-bootstrap';

const formFieldStyle = "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight border-none focus:outline-none focus:shadow-outline";

const FormField = ({ id, label, type, value, onChange }) => (
  <Form.Group className='mb-3'>
    <Form.Label htmlFor={id} className="block text-gray-700 text-sm font-bold mb-2">{label}</Form.Label>
    <Form.Control 
      type={type}
      id={id}
      value={value}
      onChange={onChange}
      required
      className={formFieldStyle}
    />
  </Form.Group>
);

export default FormField;