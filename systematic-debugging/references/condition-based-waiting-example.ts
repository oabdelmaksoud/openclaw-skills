// Complete implementation of condition-based waiting utilities
// Context: Fixed flaky tests by replacing arbitrary timeouts

/**
 * Wait for a specific event type to appear
 *
 * @param events - Array of events to search
 * @param eventType - Type of event to wait for
 * @param timeoutMs - Maximum time to wait (default 5000ms)
 * @returns Promise resolving to the first matching event
 *
 * Example:
 *   await waitForEvent(events, 'TOOL_RESULT');
 */
export function waitForEvent<T extends { type: string }>(
  getEvents: () => T[],
  eventType: string,
  timeoutMs = 5000
): Promise<T> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const events = getEvents();
      const event = events.find((e) => e.type === eventType);

      if (event) {
        resolve(event);
      } else if (Date.now() - startTime > timeoutMs) {
        reject(new Error(`Timeout waiting for ${eventType} event after ${timeoutMs}ms`));
      } else {
        setTimeout(check, 10); // Poll every 10ms for efficiency
      }
    };

    check();
  });
}

/**
 * Wait for a specific number of events of a given type
 *
 * @param getEvents - Function that returns current events
 * @param eventType - Type of event to wait for
 * @param count - Number of events to wait for
 * @param timeoutMs - Maximum time to wait (default 5000ms)
 * @returns Promise resolving to all matching events once count is reached
 *
 * Example:
 *   await waitForEventCount(getEvents, 'AGENT_MESSAGE', 2);
 */
export function waitForEventCount<T extends { type: string }>(
  getEvents: () => T[],
  eventType: string,
  count: number,
  timeoutMs = 5000
): Promise<T[]> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const events = getEvents();
      const matchingEvents = events.filter((e) => e.type === eventType);

      if (matchingEvents.length >= count) {
        resolve(matchingEvents);
      } else if (Date.now() - startTime > timeoutMs) {
        reject(
          new Error(
            `Timeout waiting for ${count} ${eventType} events after ${timeoutMs}ms (got ${matchingEvents.length})`
          )
        );
      } else {
        setTimeout(check, 10);
      }
    };

    check();
  });
}

/**
 * Wait for an event matching a custom predicate
 *
 * @param getEvents - Function that returns current events
 * @param predicate - Function that returns true when event matches
 * @param description - Human-readable description for error messages
 * @param timeoutMs - Maximum time to wait (default 5000ms)
 * @returns Promise resolving to the first matching event
 *
 * Example:
 *   await waitForEventMatch(
 *     getEvents,
 *     (e) => e.type === 'TOOL_RESULT' && e.data.id === 'call_123',
 *     'TOOL_RESULT with id=call_123'
 *   );
 */
export function waitForEventMatch<T>(
  getEvents: () => T[],
  predicate: (event: T) => boolean,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const events = getEvents();
      const event = events.find(predicate);

      if (event) {
        resolve(event);
      } else if (Date.now() - startTime > timeoutMs) {
        reject(new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`));
      } else {
        setTimeout(check, 10);
      }
    };

    check();
  });
}

/**
 * Generic condition-based waiting
 *
 * @param condition - Function that returns truthy when condition is met
 * @param description - Human-readable description for error messages
 * @param timeoutMs - Maximum time to wait (default 5000ms)
 */
export async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const startTime = Date.now();

  while (true) {
    const result = condition();
    if (result) return result;

    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }

    await new Promise(r => setTimeout(r, 10));
  }
}
