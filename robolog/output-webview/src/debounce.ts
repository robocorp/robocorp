export const debounce = (func, wait) => {
    let timeout: NodeJS.Timeout;

    return function wrapper(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };

        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};
