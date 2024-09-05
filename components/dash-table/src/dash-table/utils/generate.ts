export default function genRandomId(prefix: string, radix = 36) {
    return prefix + Math.random().toString(radix).substring(2);
}
