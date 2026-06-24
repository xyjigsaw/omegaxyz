If you are a front-end developer, the workflow is familiar:

Open Chrome on a computer.

Press F12.

And suddenly you have everything.

Inspect elements, edit CSS, monitor APIs, debug JavaScript, check Storage, read cookies, and understand what the page is doing. Chrome DevTools has become one of the most important tools in modern web development.

But one device has always felt unfinished to me:

iPad.

![iDevTools inspecting elements in Safari on iPad](https://cdn.omegaxyz.com/2026/06/idevtools-ipad-elements.webp)

*iDevTools brings a desktop-like element inspection workflow to Safari on iPad.*

## iPad Is Powerful Enough, but Safari Still Lacks DevTools

iPad hardware has become dramatically stronger over the past few years.

M-series chips, external displays, Stage Manager, desktop-class Safari... Apple has been pushing iPad closer to a real productivity machine.

But for developers, one key piece has still been missing:

developer tools.

Sometimes I only want to:

- Inspect the structure of a page
- Check a CSS rule
- See what an API returned
- Debug a small JavaScript issue
- Read localStorage, sessionStorage, or cookies

In Chrome, these tasks take seconds.

On iPad, they usually mean:

open a Mac, connect the device, launch Safari remote debugging, find the page, and only then start investigating.

The setup can be more complicated than the bug itself.

So I started asking:

What if the most commonly used parts of Chrome DevTools could run directly inside Safari?

## That Became iDevTools

iDevTools is a developer tool extension designed specifically for Safari.

The goal is not to fully clone Chrome DevTools. That would be almost impossible, and it would not necessarily fit a mobile workflow.

Instead, iDevTools focuses on the most common 80% of debugging needs, so developers can handle basic web inspection directly on iPad.

![iDevTools network request monitor and request details](https://cdn.omegaxyz.com/2026/06/idevtools-ipad-network.webp)

iDevTools currently includes these core areas:

### Elements

- DOM Tree browsing
- Element Picker
- CSS inspection
- Box Model information
- Selector copying

### Network

- Fetch request monitoring
- XHR request monitoring
- Request and response inspection
- Header analysis
- Timing information

### Console

- Console logs
- Warnings
- Errors
- Runtime exceptions

### Storage

- localStorage
- sessionStorage
- Cookies

### JavaScript

- Run JavaScript inside the page
- View evaluation results

The interface is inspired by familiar Chrome and Safari DevTools layouts. It can be docked to the right side or bottom of the page, resized for different workflows, and adapted for landscape, portrait, touch, trackpad, and keyboard usage.

## The Hardest Part Was Not Code. It Was Safari.

At first, I thought:

Safari Extension ~= Chrome Extension.

Once development started, I quickly learned that this was not true.

Safari has more constraints. Many capabilities that feel obvious in Chrome need to be redesigned for Safari.

For example:

- Content scripts are isolated from the page context
- Network capture works differently
- Manifest validation is stricter
- Extension lifecycle behavior is different
- App Store review requirements add another layer of constraints

Even uploading to the App Store revealed small manifest issues that were easy to miss:

```text
The description field must be present and 112 or fewer characters long.

The icons field is required.
```

These are not problems you usually think about in the Chrome Extension world.

But these constraints also make the product direction clearer. iDevTools should not cram every desktop browser feature into iPad. It should make the most valuable debugging paths stable, direct, and understandable.

![iDevTools running in Safari on iPhone](https://cdn.omegaxyz.com/2026/06/idevtools-iphone-console.webp)

## Why I Think This Matters

For years, iPad has been moving closer to the computer.

But the developer tooling ecosystem has lagged behind.

For developers, productivity is not only about performance. It is about tools.

If a device cannot help you debug, it is hard for that device to become a real development machine.

I do not think iPad will replace the Mac. But I do hope that when you only need to quickly inspect a page, debug an API, or check an element, you do not have to reach for a computer.

Open Safari.

Tap the extension button.

Start debugging like you would in Chrome.

That is what iDevTools is trying to make possible.

## Roadmap

The project is still under active development. Planned features include:

- HAR export
- IndexedDB viewer
- Page audits
- SEO checks
- Accessibility checks
- AI-assisted debugging

If you often use iPad and are interested in web development, debugging tools, or Safari Extensions, I would love to hear your thoughts.

## Download

- [App Store (US / English)](https://apps.apple.com/us/app/idevtools/id6782373788)
- [App Store (China)](https://apps.apple.com/cn/app/idevtools/id6782373788)

You can also read the full privacy policy: [iDevTools Privacy Policy](https://omegaxyz.com/idevtools-privacy/).
