/**
 * Inicializa estilos base
 * 1. Change from `box-sizing: content-box` so that `width` is not affected
 *    by `padding` or `border`.
 * 2. As a best practice, apply a default 'background-color'.
 * 3. Set an explicit initial text-align value so that we can later use the the 'inherit'
 *    value on things like '<th>' elements.
 * 4. Prevent adjustments of font size after orientation changes in IE on
 *    Windows Phone and in iOS.
 * 5. Setting @viewport causes scrollbars to overlap content in IE11 and Edge,
 *    so we force a non-overlapping, non-auto-hiding scrollbar to counteract.
 * 6. Change the default tap highlight to be completely transparent in iOS.
 * 7. Implement full height to let children control own height.
 */
export const reboot = `
  *,
  *::before,
  *::after {
    box-sizing: border-box;
  }

  html {
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
    -ms-overflow-style: scrollbar;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    -webkit-tap-highlight-color: transparent;
    height: 100%;
  }

  body {
    font-weight: 400;
    font-family: 'Roboto', sans-serif;
    font-size: 1rem;
    line-height: 1.5rem;
    color: #14232b;
    text-align: left;
    background-color: #f8f9fa;
    height: 100%;

    #root {
      height: 100%;
    }
  }

  -ms-viewport {
    width: device-width;
  }
`;
