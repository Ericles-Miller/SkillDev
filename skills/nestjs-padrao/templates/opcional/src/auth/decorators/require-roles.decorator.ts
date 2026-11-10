import { SetMetadata } from '@nestjs/common';
import { ERole } from '../enums/role.enum';

export const ROLES_KEY = 'roles';

// Sem @RequireRoles, qualquer usuário autenticado passa; com ele, só os papéis listados.
export const RequireRoles = (...roles: ERole[]) => SetMetadata(ROLES_KEY, roles);
