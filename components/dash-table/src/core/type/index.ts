export type OptionalMap<T, TR extends keyof T, M> = {
    [tr in TR]?: M;
};
export type RequiredPluck<T, R extends keyof T> = {[r in R]: T[r]};
export type OptionalPluck<T, R extends keyof T> = {[r in R]?: T[r]};

export type RequiredProp<T, R extends keyof T> = T[R];
export type OptionalProp<T, R extends keyof T> = T[R] | undefined;

export type PropOf<T, R extends keyof T> = R;

export type Merge<M, N> = Omit<M, Extract<keyof M, keyof N>> & N;
