export function pathBasename(source: string): string {
    let basename = source;
    let index = Math.max(source.lastIndexOf("/"), source.lastIndexOf("\\"));
    if (index > 0) {
        basename = source.substring(index + 1);
    }
    return basename;
}
