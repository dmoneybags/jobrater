export class HelperFunctions {
    /**
     * getTimeFrameSeconds
     * 
     * returns the amount of seconds in a timeFrame
     * 
     * @param {string} timeFrame: the string timeframe
     * @returns {number} the number of seconds in the timeframe
     */
    static getTimeFrameSeconds = (timeFrame: string):number => {
        let seconds: number = 0;
        switch (timeFrame) {
            case 'months':
                seconds = 7 * 24 * 3600;
                break;
            case 'month':
                seconds = 7 * 24 * 3600;
                break;
            case 'weeks':
                seconds = 7 * 24 * 3600;
                break;
            case 'week':
                seconds = 7 * 24 * 3600;
                break;
            case 'days':
                seconds = 24 * 3600;
                break;
            case 'day':
                seconds = 24 * 3600;
                break;
            case 'hours':
                seconds = 3600;
                break;
            case 'hour':
                seconds = 3600;
                break;
            case 'minutes':
                seconds = 60;
                break;
            case 'minute':
                seconds = 60;
                break;
            default:
                console.error('Unsupported timeframe');
                break;
        }
        return seconds;
    }
    static waitForDocumentLoaded = (): Promise<void> => {
        return new Promise<void>((resolve) => {
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                resolve();
            } else {
                document.addEventListener('DOMContentLoaded', () => resolve(), { once: true });
            }
        });
    }
    static async tryWithRetryPromise(task: () => Promise<any>, retries: number = 1, delay: number = 500): Promise<void> {
        try {
            return await task();
        } catch (error) {
            if (retries > 0) {
                console.log(`Retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
                return await HelperFunctions.tryWithRetryPromise(task, retries - 1, delay);
            } else {
                throw error;
            }
        }
    }
    static async tryWithRetry<T>(task: () => T, retries: number = 1, delay: number = 500): Promise<T> {
        const executeTask = async () => {
            try {
                return task();
            } catch (error) {
                if (retries > 0) {
                    console.log(`Retrying in ${delay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                    return HelperFunctions.tryWithRetry(task, retries - 1, delay);
                } else {
                    throw error;
                }
            }
        };
    
        return executeTask();
    }
}