export const MIN_SECRET_LENGTH = 32; // caracteres; gere com `openssl rand -hex 32`
export const DEFAULT_ACCESS_EXPIRES_IN = '15m'; // curto: um access token vazado vale pouco tempo
export const DEFAULT_REFRESH_EXPIRES_IN = '7d'; // quanto tempo o usuário fica logado sem digitar a senha
