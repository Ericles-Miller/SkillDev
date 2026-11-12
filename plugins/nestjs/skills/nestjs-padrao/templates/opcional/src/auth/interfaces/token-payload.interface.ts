import { ERole } from '../enums/role.enum';

export interface IAccessTokenPayload {
  sub: string;
  email: string;
  role: ERole;
}

export interface IRefreshTokenPayload {
  sub: string;
}
