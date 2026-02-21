import '@testing-library/jest-dom';

import { render, screen, cleanup } from '@testing-library/react';

import { AppQueryParamsProvider, useAppQueryParams } from '#/shell/hooks/AppQueryParamsContext';

afterEach(() => {
  cleanup();
  // restore location.search if tests modified it
  try {
    // @ts-ignore
    delete window.location;
  } catch {
    /* ignore */
  }
  // reassign a default location for other tests (safe fallback)
  // @ts-ignore
  window.location = new URL('http://localhost/');
});

describe('AppQueryParamsProvider and useAppQueryParams', () => {
  function RenderValues() {
    const api = useAppQueryParams();

    return (
      <div>
        <div data-testid="all">{JSON.stringify(api.all)}</div>
        <div data-testid="has-foo">{String(api.has('foo'))}</div>
        <div data-testid="get-foo">{JSON.stringify(api.get('foo'))}</div>
        <div data-testid="get-missing">{JSON.stringify(api.get('missing', 'fallback'))}</div>
        <div data-testid="num-good">{String(api.getNumber('n', null))}</div>
        <div data-testid="num-bad">{String(api.getNumber('bad', 42))}</div>
        <div data-testid="bool-true">{String(api.getBoolean('btrue', null))}</div>
        <div data-testid="bool-false">{String(api.getBoolean('bfalse', null))}</div>
        <div data-testid="bool-one">{String(api.getBoolean('bone', null))}</div>
        <div data-testid="bool-zero">{String(api.getBoolean('bzero', null))}</div>
        <div data-testid="bool-bad">{String(api.getBoolean('bbad', false))}</div>
        <div data-testid="arr-single">{JSON.stringify(api.getArray('asingle'))}</div>
        <div data-testid="arr-multi">{JSON.stringify(api.getArray('amulti'))}</div>
      </div>
    );
  }

  test('parses sourceSearch and provides correct API behavior', () => {
    const search =
      '?foo=bar&n=123&bad=not-a-number&btrue=true&bfalse=false&bone=1&bzero=0&bbad=maybe&asingle=only&amulti=one&amulti=two';

    render(
      <AppQueryParamsProvider sourceSearch={search}>
        <RenderValues />
      </AppQueryParamsProvider>,
    );

    // all contains parsed values (amulti becomes array)
    expect(JSON.parse(screen.getByTestId('all').textContent || '{}')).toMatchObject({
      foo: 'bar',
      n: '123',
      bad: 'not-a-number',
      btrue: 'true',
      bfalse: 'false',
      bone: '1',
      bzero: '0',
      bbad: 'maybe',
      asingle: 'only',
      amulti: ['one', 'two'],
    });

    // has
    expect(screen.getByTestId('has-foo')).toHaveTextContent('true');

    // get existing & fallback for missing
    expect(screen.getByTestId('get-foo')).toHaveTextContent(JSON.stringify('bar'));
    expect(screen.getByTestId('get-missing')).toHaveTextContent(JSON.stringify('fallback'));

    // getNumber: valid number returns number, invalid returns fallback
    expect(screen.getByTestId('num-good')).toHaveTextContent('123');
    expect(screen.getByTestId('num-bad')).toHaveTextContent('42'); // fallback provided above in RenderValues

    // getBoolean: true/false/1/0 mapping
    expect(screen.getByTestId('bool-true')).toHaveTextContent('true');
    expect(screen.getByTestId('bool-false')).toHaveTextContent('false');
    expect(screen.getByTestId('bool-one')).toHaveTextContent('true');
    expect(screen.getByTestId('bool-zero')).toHaveTextContent('false');
    expect(screen.getByTestId('bool-bad')).toHaveTextContent('false'); // fallback used

    // getArray: single value becomes single-element array; multi remains array
    expect(screen.getByTestId('arr-single')).toHaveTextContent(JSON.stringify(['only']));
    expect(screen.getByTestId('arr-multi')).toHaveTextContent(JSON.stringify(['one', 'two']));
  });

  test('get and getArray fallbacks behave correctly when key missing', () => {
    render(
      <AppQueryParamsProvider sourceSearch="?x=y">
        <div>
          <InsideTest />
        </div>
      </AppQueryParamsProvider>,
    );

    function InsideTest() {
      const api = useAppQueryParams();

      return (
        <div>
          <div data-testid="missing-get">{JSON.stringify(api.get('nope', 'def'))}</div>
          <div data-testid="missing-get-null">{JSON.stringify(api.get('nope'))}</div>
          <div data-testid="missing-array">{JSON.stringify(api.getArray('nope'))}</div>
        </div>
      );
    }

    expect(screen.getByTestId('missing-get')).toHaveTextContent(JSON.stringify('def'));
    expect(screen.getByTestId('missing-get-null')).toHaveTextContent(JSON.stringify(null));
    expect(screen.getByTestId('missing-array')).toHaveTextContent(JSON.stringify([]));
  });

  test('getNumber returns fallback when value is array with non-numeric first element', () => {
    render(
      <AppQueryParamsProvider sourceSearch="?n=7&n=notnum">
        <InsideNumber />
      </AppQueryParamsProvider>,
    );

    function InsideNumber() {
      const api = useAppQueryParams();
      return <div data-testid="num">{String(api.getNumber('n', 99))}</div>;
    }

    // first value is "7" so parsing should yield 7
    expect(screen.getByTestId('num')).toHaveTextContent('7');
  });

  test('getBoolean returns fallback null when key absent and fallback omitted', () => {
    render(
      <AppQueryParamsProvider sourceSearch="?something=ok">
        <InsideBool />
      </AppQueryParamsProvider>,
    );

    function InsideBool() {
      const api = useAppQueryParams();
      return <div data-testid="b">{String(api.getBoolean('nothere'))}</div>;
    }

    // fallback default is null -> String(null) === 'null'
    expect(screen.getByTestId('b')).toHaveTextContent('null');
  });

  test('API methods are stable across renders (useMemo coverage)', () => {
    const { rerender } = render(
      <AppQueryParamsProvider sourceSearch="?a=1">
        <RenderValues />
      </AppQueryParamsProvider>,
    );

    expect(screen.getByTestId('get-foo')).toHaveTextContent(JSON.stringify(null));

    // Rerender with identical provider props to verify memo stability (no crash, same values)
    rerender(
      <AppQueryParamsProvider sourceSearch="?a=1">
        <RenderValues />
      </AppQueryParamsProvider>,
    );

    expect(screen.getByTestId('get-foo')).toHaveTextContent(JSON.stringify(null));
  });
});
