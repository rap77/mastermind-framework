# MasterMind Mobile Features

MasterMind is fully responsive and optimized for mobile devices. This guide covers mobile-specific features and behaviors.

## Responsive Design

MasterMind adapts to different screen sizes:

- **Desktop** (≥ 768px): Three-column layout with sidebar navigation
- **Mobile** (< 768px): Single-column layout with bottom navigation

## Bottom Navigation

On mobile devices, the sidebar is replaced with a fixed bottom navigation bar:

### Navigation Items

1. **War Room** (`/war-room`): Command center dashboard
2. **Nexus** (`/nexus`): Browse and trigger expert brains
3. **Strategy** (`/strategy`): Planning and prioritization tools
4. **Settings** (`/settings`): Configure preferences and API keys

### Active State

The current page is highlighted with an accent color for easy orientation.

### Accessibility

- Touch targets: 44x44px minimum (WCAG 2.1 Level A)
- ARIA labels for screen readers
- Keyboard navigation support

## Command Palette on Mobile

The command palette (`Cmd+K` / `Ctrl+K`) works on mobile devices:

### Mobile Keyboard Shortcuts

- **Android**: `Ctrl+K` (requires external keyboard)
- **iOS**: `Cmd+K` (requires external keyboard)

### Alternative Access

For touch-only interactions:

1. Tap the search icon (if available in the UI)
2. Use the navigation menu to access different sections

## Onboarding on Mobile

The onboarding wizard is fully optimized for mobile:

### 3-Step Process

1. **Welcome**: Feature overview with `Cmd+K` hint
2. **Company & Adapter**: Setup form (stacked layout)
3. **Validation**: Test adapter connection
4. **Complete**: Success message with auto-redirect

### Mobile-Specific Optimizations

- Single-column layout
- Larger touch targets (44x44px minimum)
- Simplified form inputs
- Progress indicator with dots

## Touch Interactions

### Button Actions

All interactive elements support touch:

- **Tap**: Execute primary action
- **Long press**: Context menu (where available)
- **Swipe**: Not yet implemented (planned for v3.1)

### Gesture Support (Future)

In v3.1, we plan to add:

- Swipe gestures for navigation
- Pull-to-refresh
- Pinch-to-zoom for certain views

## Performance

Mobile performance optimizations:

- **Lazy loading**: Components load on-demand
- **Code splitting**: Reduced initial bundle size
- **Image optimization**: Responsive images
- **Debouncing**: Reduced state updates

## Browser Compatibility

### Supported Mobile Browsers

- **iOS Safari**: iOS 14+
- **Chrome Mobile**: Android 8+
- **Firefox Mobile**: Latest version
- **Edge Mobile**: Latest version

### Known Issues

- **iOS Safari**: Some keyboard shortcuts require external keyboard
- **Android Chrome`: `Ctrl+K` may conflict with browser shortcuts

## Testing

Mobile features are tested on:

- **Emulators**: iOS Simulator, Android Emulator
- **Real devices**: iPhone 12+, Pixel 5+ (planned for v3.1 with BrowserStack)

## Accessibility

MasterMind mobile meets WCAG 2.1 Level A standards:

- ✅ Touch targets ≥ 44x44px
- ✅ Sufficient color contrast (3:1 for large text)
- ✅ Screen reader support (VoiceOver, TalkBack)
- ✅ Keyboard navigation (external keyboard)
- ✅ Focus indicators

## Tips for Mobile Users

1. **Use Bottom Navigation**: Quick access to main sections
2. **Landscape Mode**: Better for data-heavy views (Cost Dashboard, etc.)
3. **External Keyboard**: Full keyboard shortcut support
4. **Pin to Home Screen**: Add to home screen for app-like experience

## Feedback

Mobile features are continuously improving. Please report issues or suggest improvements via the feedback link in Settings.
