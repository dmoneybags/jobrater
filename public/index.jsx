import React, { createElement } from 'react';
import ReactDOM from 'react-dom';
import { createRoot } from 'react-dom/client';
import { RegisterForm, LoginForm } from '../src/content/tests/testLogin';

const App = () => {
    return (
      <div>
        <RegisterForm />
        <LoginForm />
      </div>
    );
};
const container = document.getElementById('app');
console.log(container)
const root = createRoot(container);
root.render(<App />);