import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the trading dashboard', () => {
  render(<App />);
  expect(screen.getByText(/smart stock trading dashboard/i)).toBeInTheDocument();
});
