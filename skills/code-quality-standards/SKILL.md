---
name: code-quality-standards
description: Enforce code quality standards including minimalism, proper comments, correctness over optimization, and eliminating unnecessary complexity. Use when writing code, refactoring, code review, or when user mentions code quality, clean code, optimization, or comments.
version: 1.0.0
---

# Code Quality Standards

Comprehensive code quality standards focused on minimalism, clarity, and correctness.

## Core Principles

### 1. Correctness First, Optimization Later

**Always check: Is the code even working correctly?**

**If NO:**
- Fix correctness first before anything else
- Don't optimize broken code
- Focus on making it work properly

**If YES:**
- Measure before you optimize anything
- Default stance: No premature optimization, period
- Only optimize when performance issues are proven

**Example:**

```typescript
// ❌ WRONG: Optimizing before it works correctly
function calculateTotal(items: any[]) {
  // Using fancy reduce for "performance" but has bug
  return items.reduce((sum, item) => sum + item.price, 0);
  // BUG: Doesn't handle null prices
}

// ✅ RIGHT: Make it work correctly first
function calculateTotal(items: Item[]): number {
  let total = 0;
  for (const item of items) {
    if (item.price != null) {
      total += item.price;
    }
  }
  return total;
}

// Then measure if performance is actually an issue
// Only optimize if measurements show it's needed
```

## Code Minimalism

**Goal: Less code, same functionality**

### Principle: Every Line Must Justify Its Existence

**Bad - Verbose:**
```typescript
function getUserName(user: User): string {
  if (user !== null && user !== undefined) {
    if (user.name !== null && user.name !== undefined) {
      if (user.name.length > 0) {
        return user.name;
      } else {
        return 'Anonymous';
      }
    } else {
      return 'Anonymous';
    }
  } else {
    return 'Anonymous';
  }
}
```

**Good - Minimal:**
```typescript
function getUserName(user: User | null): string {
  return user?.name || 'Anonymous';
}
```

### Remove Unnecessary Abstractions

**Bad - Over-abstracted:**
```typescript
interface IUserNameGetter {
  getName(): string;
}

class UserNameGetterFactory {
  static create(user: User): IUserNameGetter {
    return new UserNameGetter(user);
  }
}

class UserNameGetter implements IUserNameGetter {
  constructor(private user: User) {}

  getName(): string {
    return this.user.name;
  }
}

// Usage
const getter = UserNameGetterFactory.create(user);
const name = getter.getName();
```

**Good - Simple:**
```typescript
function getUserName(user: User): string {
  return user.name;
}

// Usage
const name = getUserName(user);
```

### Clean and Powerful Over Verbose and Complex

**Bad:**
```typescript
function processUserData(userData: any) {
  const processedData = {
    id: userData.id,
    name: userData.name,
    email: userData.email
  };

  if (userData.profile) {
    processedData.profile = {
      bio: userData.profile.bio,
      avatar: userData.profile.avatar
    };
  }

  if (userData.settings) {
    processedData.settings = {
      theme: userData.settings.theme,
      notifications: userData.settings.notifications
    };
  }

  return processedData;
}
```

**Good:**
```typescript
function processUserData({ id, name, email, profile, settings }: UserData): ProcessedUser {
  return {
    id,
    name,
    email,
    ...(profile && { profile: { bio: profile.bio, avatar: profile.avatar } }),
    ...(settings && { settings: { theme: settings.theme, notifications: settings.notifications } })
  };
}
```

### Exact Functionality Only, No Extra Features

**Bad - Adding unused features "just in case":**
```typescript
interface UserService {
  getUser(id: string): Promise<User>;
  getAllUsers(): Promise<User[]>; // Not needed yet
  searchUsers(query: string): Promise<User[]>; // Not needed yet
  updateUser(id: string, data: Partial<User>): Promise<User>; // Not needed yet
  deleteUser(id: string): Promise<void>; // Not needed yet
}
```

**Good - Only what's needed now:**
```typescript
interface UserService {
  getUser(id: string): Promise<User>;
}

// Add other methods only when actually needed
```

## Code Comments

### Comment Format: "//comment here..."

**Use inline comment format:**
```typescript
// Good
// This function calculates the total price including tax

/* Bad - avoid block comments unless absolutely necessary */
/* This function calculates
   the total price
   including tax */
```

### Comment Length: 1-3 Lines Max Per Block

**Bad - Too long:**
```typescript
// This function is responsible for processing user authentication
// by first validating the credentials against the database, then
// checking if the user has the necessary permissions, after which
// it generates a JWT token with appropriate claims and expiration
// time, and finally it logs the authentication event for security
// auditing purposes before returning the token to the caller
function authenticate(credentials: Credentials): Promise<AuthResult> {
  // ...
}
```

**Good - Concise:**
```typescript
// Validates credentials, generates JWT token, and logs auth event
function authenticate(credentials: Credentials): Promise<AuthResult> {
  // ...
}
```

### Explain Purpose and Functionality Clearly

**Bad - Vague:**
```typescript
// Process data
function processData(data: unknown) { }

// Check stuff
if (user.age > 18) { }
```

**Good - Clear:**
```typescript
// Validates and transforms user input into database format
function processData(data: unknown): DatabaseRecord { }

// Verify user is adult for age-restricted content
if (user.age > 18) { }
```

### Professional and Standard Style

**Bad - Informal:**
```typescript
// lol this is a hack but it works
// TODO: fix this mess later maybe???
// idk why this is needed but don't remove it!!!
```

**Good - Professional:**
```typescript
// Temporary workaround for API v1 compatibility
// TODO: Remove after migrating to API v2 (PROJ-123)
// Required for backwards compatibility with legacy clients
```

### Avoid Super Short Comments That Don't Explain Anything

**Bad - Useless:**
```typescript
// Get user
const user = await getUser(id);

// Set name
user.name = newName;

// Save
await saveUser(user);
```

**Good - Meaningful:**
```typescript
// Fetch user from database to ensure latest data
const user = await getUser(id);

// Update display name (validates against profanity filter)
user.name = sanitizeName(newName);

// Persist changes and trigger name change notifications
await saveUser(user);
```

### Make Code Easy to Understand Through Meaningful Comments

**Example:**
```typescript
// Calculate daily usage limit reset time
// Users get fresh credits at midnight UTC
const resetTime = new Date();
resetTime.setUTCHours(24, 0, 0, 0);

// Check if user exceeded their daily API quota
// Free tier: 100 requests, Pro tier: 1000 requests
const isOverQuota = user.dailyRequests >= getTierLimit(user.tier);

// Apply exponential backoff to prevent rapid retry storms
// Formula: baseDelay * (2 ^ retryCount) with max 60s
const backoffDelay = Math.min(
  BASE_RETRY_DELAY * Math.pow(2, retryCount),
  MAX_RETRY_DELAY
);
```

## Code Quality Checklist

Before committing any code:

### Correctness
- [ ] Code works correctly for all expected inputs
- [ ] Edge cases are handled
- [ ] Error handling is comprehensive
- [ ] No bugs or logical errors

### Minimalism
- [ ] No unnecessary lines or abstractions
- [ ] Every line justifies its existence
- [ ] No "just in case" code
- [ ] No premature optimization
- [ ] No unused variables or functions
- [ ] No duplicate code

### Comments
- [ ] Comments use "//comment" format
- [ ] Each comment block is 1-3 lines max
- [ ] Comments explain purpose and functionality
- [ ] Professional and standard style
- [ ] No vague or useless comments
- [ ] Complex logic is well-documented

### Clarity
- [ ] Code is self-documenting where possible
- [ ] Variable names are descriptive
- [ ] Function names describe what they do
- [ ] Logic is easy to follow
- [ ] No clever tricks that sacrifice readability

## Common Patterns

### Simplify Conditional Logic

**Bad:**
```typescript
function canAccessFeature(user: User): boolean {
  if (user.isPremium === true) {
    return true;
  } else {
    if (user.trialActive === true) {
      return true;
    } else {
      return false;
    }
  }
}
```

**Good:**
```typescript
function canAccessFeature(user: User): boolean {
  return user.isPremium || user.trialActive;
}
```

### Reduce Nesting

**Bad:**
```typescript
function processOrder(order: Order) {
  if (order.isValid) {
    if (order.isPaid) {
      if (order.items.length > 0) {
        // Process order
        return processItems(order.items);
      }
    }
  }
  return null;
}
```

**Good:**
```typescript
function processOrder(order: Order) {
  // Early returns reduce nesting
  if (!order.isValid) return null;
  if (!order.isPaid) return null;
  if (order.items.length === 0) return null;

  // Main logic at top level
  return processItems(order.items);
}
```

### Extract Complex Conditions

**Bad:**
```typescript
if (user.age >= 18 && user.hasVerifiedEmail && !user.isBanned && user.acceptedTerms) {
  // Allow access
}
```

**Good:**
```typescript
// Extract to named function that explains intent
function canAccessAdultContent(user: User): boolean {
  return (
    user.age >= 18 &&
    user.hasVerifiedEmail &&
    !user.isBanned &&
    user.acceptedTerms
  );
}

if (canAccessAdultContent(user)) {
  // Allow access
}
```

### Avoid Premature Optimization

**Bad:**
```typescript
// "Optimizing" by caching before knowing if it's needed
const cache = new Map<string, User>();

function getUser(id: string): User {
  if (cache.has(id)) {
    return cache.get(id)!;
  }
  const user = fetchUser(id);
  cache.set(id, user);
  return user;
}
```

**Good:**
```typescript
// Simple and correct first
function getUser(id: string): User {
  return fetchUser(id);
}

// Add caching ONLY if measurements show it's needed
// And only after proving correctness
```

### Remove Dead Code

**Bad:**
```typescript
function calculatePrice(item: Item): number {
  // Old calculation
  // const basePrice = item.price * 1.1;
  // const tax = basePrice * 0.08;
  // return basePrice + tax;

  // New calculation
  return item.price * 1.18;

  // Keeping old code "just in case"
}
```

**Good:**
```typescript
function calculatePrice(item: Item): number {
  // Price includes 18% markup (10% margin + 8% tax)
  return item.price * 1.18;
}

// Old code deleted - version control keeps history if needed
```

## Anti-Patterns to Avoid

### Don't Write "Clever" Code

**Bad:**
```typescript
// Too clever - hard to understand
const result = arr.reduce((a, b) => a.concat(b.map(c => c.split(',').filter(d => d))), []);
```

**Good:**
```typescript
// Clear and readable
const result: string[] = [];
for (const item of arr) {
  for (const value of item) {
    const parts = value.split(',').filter(part => part.trim());
    result.push(...parts);
  }
}
```

### Don't Add Unnecessary Layers

**Bad:**
```typescript
class UserRepository {
  async getUser(id: string): Promise<User> {
    return this.database.users.findById(id);
  }
}

class UserService {
  constructor(private repo: UserRepository) {}

  async getUser(id: string): Promise<User> {
    return this.repo.getUser(id);
  }
}

class UserController {
  constructor(private service: UserService) {}

  async getUser(id: string): Promise<User> {
    return this.service.getUser(id);
  }
}
```

**Good:**
```typescript
// Only add layers when they provide actual value
async function getUser(id: string): Promise<User> {
  return database.users.findById(id);
}

// Add service layer only when business logic is needed
```

### Don't Optimize Before Measuring

**Bad:**
```typescript
// Micro-optimizing without measurements
const result = [];
const len = arr.length; // "Faster" to cache length
for (let i = 0; i < len; ++i) { // Using ++i "for performance"
  result.push(arr[i]);
}
```

**Good:**
```typescript
// Clear code first, optimize only if proven needed
const result = [];
for (const item of arr) {
  result.push(item);
}

// Or even simpler
const result = [...arr];
```

## Summary: Quality Over Quantity

**Core Values:**
1. **Correctness First** - Make it work right before making it fast
2. **Minimalism** - Less code, same functionality
3. **Clarity** - Clean and powerful over verbose and complex
4. **Meaningful Comments** - Explain why and how, not what
5. **No Premature Optimization** - Measure before optimizing
6. **Every Line Counts** - Each line must justify its existence

**Remember:** The best code is code that doesn't need to exist. The second best is code that's simple, correct, and easy to understand.
