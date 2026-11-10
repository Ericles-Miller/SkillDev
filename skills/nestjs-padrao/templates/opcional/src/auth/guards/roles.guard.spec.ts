import { ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { RequireRoles } from '../decorators/require-roles.decorator';
import { ERole } from '../enums/role.enum';
import { AuthenticatedRequest, IAuthenticatedUser } from '../interfaces/authenticated-user.interface';
import { RolesGuard } from './roles.guard';

const guard = new RolesGuard(new Reflector());

function contextFor(user: IAuthenticatedUser | undefined, roles?: ERole[]): ExecutionContext {
  const handler = () => undefined;
  if (roles) RequireRoles(...roles)(handler);
  const request = { user } as AuthenticatedRequest;

  return {
    getHandler: () => handler,
    getClass: () => class TestController {},
    switchToHttp: () => ({ getRequest: () => request }),
  } as unknown as ExecutionContext;
}

const admin: IAuthenticatedUser = { id: 'user-1', email: 'ana@example.com', role: ERole.ADMIN };
const user: IAuthenticatedUser = { id: 'user-2', email: 'bia@example.com', role: ERole.USER };

describe('RolesGuard', () => {
  it('lets any authenticated user through when the route requires no role', () => {
    expect(guard.canActivate(contextFor(user))).toBe(true);
  });

  it('lets a user with one of the required roles through', () => {
    expect(guard.canActivate(contextFor(admin, [ERole.ADMIN]))).toBe(true);
  });

  it('rejects a user without the required role', () => {
    expect(() => guard.canActivate(contextFor(user, [ERole.ADMIN]))).toThrow(ForbiddenException);
  });

  it('rejects a request without a user when the route requires a role', () => {
    expect(() => guard.canActivate(contextFor(undefined, [ERole.USER]))).toThrow(ForbiddenException);
  });
});
