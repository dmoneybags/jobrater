import React, { createElement } from 'react';
import ReactDOM from 'react-dom';
import { createRoot } from 'react-dom/client';
import { RegisterForm, LoginForm } from '../src/tests/testLoginReact';

const App = () => {
    return (
      <div>
        <RegisterForm />
        <LoginForm />
      </div>
    );
};
const container = document.getElementById('app');
const root = createRoot(container);
root.render(<App />);