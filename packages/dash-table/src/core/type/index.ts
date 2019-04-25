export type RequiredPluck<T, R extends keyof T> = { [r in R]: T[r] };
export type OptionalPluck<T, R extends keyof T> = { [r in R]?: T[r] };
