import React from 'react'
import { render, screen } from '@testing-library/react'
import ErrorBoundary from '../ErrorBoundary'

class Crashy extends React.Component {
  render(): React.ReactNode {
    throw new Error('boom')
  }
}

describe('ErrorBoundary', () => {
  it('renders fallback UI on render crash', () => {
    render(
      <ErrorBoundary>
        <Crashy />
      </ErrorBoundary>
    )

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
  })
})
