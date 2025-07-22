# MCP Puppeteer Usage Guide

This guide covers how to use MCP Puppeteer for automated testing, performance analysis, and debugging of your MinRights application.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Performance Testing](#performance-testing)
- [UI/UX Testing](#uiux-testing)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Basic Usage

### 1. Navigation
```javascript
// Navigate to your application
await mcp__puppeteer__puppeteer_navigate({
  url: "http://localhost:3000"
});

// Navigate with custom launch options if needed
await mcp__puppeteer__puppeteer_navigate({
  url: "http://localhost:3000",
  launchOptions: {
    headless: true
  }
});
```

### 2. Taking Screenshots
```javascript
// Basic screenshot
await mcp__puppeteer__puppeteer_screenshot({
  name: "homepage"
});

// Screenshot with custom dimensions
await mcp__puppeteer__puppeteer_screenshot({
  name: "fullscreen-test",
  width: 1920,
  height: 1080
});

// Screenshot of specific element
await mcp__puppeteer__puppeteer_screenshot({
  name: "map-only",
  selector: ".maplibregl-map"
});
```

### 3. Interactions
```javascript
// Click elements
await mcp__puppeteer__puppeteer_click({
  selector: "button"
});

// Fill input fields
await mcp__puppeteer__puppeteer_fill({
  selector: "input[type='text']",
  value: "test value"
});

// Hover over elements
await mcp__puppeteer__puppeteer_hover({
  selector: ".map-control"
});

// Select dropdown options
await mcp__puppeteer__puppeteer_select({
  selector: "select",
  value: "option-value"
});
```

## Performance Testing

### Basic Performance Analysis
```javascript
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    const performanceData = {};
    
    if (performance && performance.timing) {
      const timing = performance.timing;
      performanceData.pageLoad = {
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
        pageLoad: timing.loadEventEnd - timing.navigationStart,
        networkTime: timing.responseEnd - timing.requestStart
      };
    }
    
    return performanceData;
  })()`
});
```

### Memory Usage Analysis
```javascript
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    if (performance && performance.memory) {
      return {
        usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + ' MB',
        totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + ' MB',
        jsHeapSizeLimit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024) + ' MB'
      };
    }
    return { error: 'Memory API not available' };
  })()`
});
```

### Resource Loading Analysis
```javascript
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    const resourceEntries = performance.getEntriesByType('resource');
    const slowResources = resourceEntries.filter(resource => resource.duration > 1000);
    
    return {
      totalResources: resourceEntries.length,
      slowResourcesCount: slowResources.length,
      slowResources: slowResources.map(r => ({
        name: r.name.split('/').pop(),
        duration: Math.round(r.duration),
        size: r.transferSize || 'Unknown'
      }))
    };
  })()`
});
```

## UI/UX Testing

### Map Functionality Testing
```javascript
// Test map zoom
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return { error: 'No canvas found' };

    const wheelEvent = new WheelEvent('wheel', {
      deltaY: -100, // Negative for zoom in
      clientX: canvas.width / 2,
      clientY: canvas.height / 2,
      bubbles: true
    });
    
    canvas.dispatchEvent(wheelEvent);
    return { zoomTestTriggered: true };
  })()`
});
```

### Accessibility Testing
```javascript
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    const images = document.querySelectorAll('img');
    const imagesWithoutAlt = Array.from(images).filter(img => !img.alt || img.alt.trim() === '');
    
    const buttons = document.querySelectorAll('button');
    const buttonsWithoutAriaLabel = Array.from(buttons).filter(btn => 
      !btn.getAttribute('aria-label') && !btn.textContent.trim()
    );

    return {
      totalImages: images.length,
      imagesWithoutAlt: imagesWithoutAlt.length,
      totalButtons: buttons.length,
      buttonsWithoutAriaLabel: buttonsWithoutAriaLabel.length,
      hasMainLandmark: !!document.querySelector('main')
    };
  })()`
});
```

### Dark/Light Mode Testing
```javascript
// Test theme switching
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    const currentScheme = document.documentElement.getAttribute('data-mantine-color-scheme');
    
    // Toggle theme (if toggle exists)
    const themeToggle = document.querySelector('[data-testid="theme-toggle"]') || 
                       document.querySelector('button[aria-label*="theme"]');
    
    if (themeToggle) {
      themeToggle.click();
    }
    
    return {
      currentScheme,
      themeToggleFound: !!themeToggle
    };
  })()`
});
```

## Common Use Cases

### 1. Full Application Health Check
```javascript
// Navigate to app
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:3000" });

// Wait for load and take screenshot
await mcp__puppeteer__puppeteer_screenshot({ name: "health-check" });

// Check for errors and performance
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    return {
      readyState: document.readyState,
      errorElements: document.querySelectorAll('[class*="error"]').length,
      loadingElements: document.querySelectorAll('[class*="loading"]').length,
      mapLoaded: !!document.querySelector('canvas')
    };
  })()`
});
```

### 2. API Response Time Testing
```javascript
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    const startTime = performance.now();
    
    return fetch('/api/maps/display_states')
      .then(response => {
        const endTime = performance.now();
        return {
          responseTime: Math.round(endTime - startTime),
          status: response.status,
          ok: response.ok
        };
      })
      .catch(error => ({
        error: error.message,
        responseTime: Math.round(performance.now() - startTime)
      }));
  })()`
});
```

### 3. User Journey Testing
```javascript
// Test complete user flow
// 1. Navigate to homepage
await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:3000" });

// 2. Take initial screenshot
await mcp__puppeteer__puppeteer_screenshot({ name: "step-1-homepage" });

// 3. Click on map area
await mcp__puppeteer__puppeteer_click({ selector: "canvas" });

// 4. Take screenshot after interaction
await mcp__puppeteer__puppeteer_screenshot({ name: "step-2-map-clicked" });

// 5. Test zoom functionality
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    const canvas = document.querySelector('canvas');
    const wheelEvent = new WheelEvent('wheel', { deltaY: -100, bubbles: true });
    canvas.dispatchEvent(wheelEvent);
    return { zoomTested: true };
  })()`
});

// 6. Final screenshot
await mcp__puppeteer__puppeteer_screenshot({ name: "step-3-after-zoom" });
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Chrome Not Found Error
```
Error: Could not find Chrome (ver. 131.0.6778.204)
```

**Solution:** Contact your system administrator or refer to your project's setup documentation.

#### 2. Navigation Timeout
**Issue:** Page takes too long to load

**Solution:**
```javascript
await mcp__puppeteer__puppeteer_navigate({
  url: "http://localhost:3000",
  launchOptions: {
    timeout: 60000  // Increase timeout to 60 seconds
  }
});
```

#### 3. Element Not Found
**Issue:** `Failed to click element: No element found`

**Solution:**
```javascript
// Wait for element to load first
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    return new Promise(resolve => {
      const checkElement = () => {
        const element = document.querySelector('your-selector');
        if (element) {
          resolve({ found: true });
        } else {
          setTimeout(checkElement, 100);
        }
      };
      checkElement();
    });
  })()`
});

// Then click
await mcp__puppeteer__puppeteer_click({ selector: "your-selector" });
```

#### 4. Screenshot Issues
**Issue:** Screenshots are blank or cut off

**Solution:**
```javascript
// Wait for content to load
await mcp__puppeteer__puppeteer_evaluate({
  script: `new Promise(resolve => setTimeout(resolve, 2000))`
});

// Then take screenshot with full dimensions
await mcp__puppeteer__puppeteer_screenshot({
  name: "full-page",
  width: 1920,
  height: 1080
});
```

## Best Practices

### 1. Wait for Application to Load
```javascript
// Wait for DOM to be ready
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    return new Promise(resolve => {
      if (document.readyState === 'complete') {
        resolve({ ready: true });
      } else {
        window.addEventListener('load', () => resolve({ ready: true }));
      }
    });
  })()`
});
```

### 2. Use Descriptive Screenshot Names
```javascript
// Bad
await mcp__puppeteer__puppeteer_screenshot({ name: "test1" });

// Good
await mcp__puppeteer__puppeteer_screenshot({ name: "homepage-after-map-load" });
```

### 3. Handle Errors Gracefully
```javascript
await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    try {
      // Your test code here
      return { success: true, data: someData };
    } catch (error) {
      return { success: false, error: error.message };
    }
  })()`
});
```

### 4. Test Responsive Design
```javascript
// Test different viewport sizes
const viewports = [
  { width: 375, height: 667 },   // Mobile
  { width: 768, height: 1024 },  // Tablet
  { width: 1920, height: 1080 }  // Desktop
];

for (const viewport of viewports) {
  await mcp__puppeteer__puppeteer_screenshot({
    name: `responsive-${viewport.width}x${viewport.height}`,
    width: viewport.width,
    height: viewport.height
  });
}
```

### 5. Monitor Performance Over Time
```javascript
// Create performance baseline
const performanceBaseline = await mcp__puppeteer__puppeteer_evaluate({
  script: `(() => {
    return {
      timestamp: new Date().toISOString(),
      pageLoad: performance.timing.loadEventEnd - performance.timing.navigationStart,
      domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
      memoryUsage: performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) : null
    };
  })()`
});

// Compare against baseline in future tests
```

## Integration with Development Workflow

### Pre-commit Testing
Create a script to run basic health checks before commits:

```javascript
// Basic health check script
const healthCheck = async () => {
  await mcp__puppeteer__puppeteer_navigate({ url: "http://localhost:3000" });
  
  const results = await mcp__puppeteer__puppeteer_evaluate({
    script: `(() => {
      return {
        loaded: document.readyState === 'complete',
        mapPresent: !!document.querySelector('canvas'),
        noErrors: document.querySelectorAll('[class*="error"]').length === 0,
        performance: performance.timing.loadEventEnd - performance.timing.navigationStart < 10000
      };
    })()`
  });
  
  return results;
};
```

### CI/CD Integration
Use Puppeteer tests in your continuous integration pipeline to catch regressions early.

---

This guide should help you effectively use MCP Puppeteer for testing and debugging your MinRights application. Remember to always start your development server before running Puppeteer tests!