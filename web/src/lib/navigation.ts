type ClearAuthFn = () => void;

export const navigation: { clearAuth: ClearAuthFn } = {
  clearAuth: () => {},
};

export function setClearAuth(fn: ClearAuthFn): void {
  navigation.clearAuth = fn;
}
