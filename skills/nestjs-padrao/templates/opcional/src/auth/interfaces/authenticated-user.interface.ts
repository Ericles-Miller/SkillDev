import { Request } from 'express';
import { ERole } from '../enums/role.enum';

export interface IAuthenticatedUser {
  id: string;
  email: string;
  role: ERole;
}

export type AuthenticatedRequest = Request & { user?: IAuthenticatedUser };
