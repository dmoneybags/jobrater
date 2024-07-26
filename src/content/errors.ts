export class ScrapingError extends Error {
    constructor(message) {
      super(message);
      this.name = 'ScrapingError';
      if (Error.captureStackTrace) {
        Error.captureStackTrace(this, ScrapingError);
      }
    }
  }
export class GlassdoorScraperError extends Error {
    constructor(message) {
        super(message);
        this.name = 'GlassdoorScraperError';
        if (Error.captureStackTrace) {
        Error.captureStackTrace(this, GlassdoorScraperError);
        }
    }
}
export class UserNotFoundError extends Error {
    constructor(message) {
        super(message);
        this.name = 'UserNotFoundError';
        if (Error.captureStackTrace) {
        Error.captureStackTrace(this, UserNotFoundError);
        }
    }
}