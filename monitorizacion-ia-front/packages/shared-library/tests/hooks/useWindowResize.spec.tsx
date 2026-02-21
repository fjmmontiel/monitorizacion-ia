import '@testing-library/jest-dom';

import { renderHook, fireEvent } from '@testing-library/react';

import { useWindowResize } from '../../src';

describe('useWindowResize()', () => {
  test('should initialize with current window size', () => {
    window.innerWidth = 1000;
    window.innerHeight = 1000;

    const { result } = renderHook(useWindowResize);
    expect(result.current.height).toEqual(1000);
    expect(result.current.width).toEqual(1000);
  });

  test('should update window size when resize window', () => {
    window.innerWidth = 1000;
    window.innerHeight = 1000;

    const { result } = renderHook(useWindowResize);
    expect(result.current.height).toEqual(1000);
    expect(result.current.width).toEqual(1000);

    fireEvent.resize(window, { target: { innerWidth: 2000, innerHeight: 2000 } });
  });
});
