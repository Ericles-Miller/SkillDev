import { ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Reflector } from '@nestjs/core';
import { JwtService } from '@nestjs/jwt';
import { Public } from '../decorators/public.decorator';
import { ERole } from '../enums/role.enum';
import { AuthenticatedRequest } from '../interfaces/authenticated-user.interface';
import { TokenService } from '../token.service';
import { JwtAuthGuard } from './jwt-auth.guard';

const tokenService = new TokenService(
  new JwtService(),
  new ConfigService({ JWT_ACCESS_SECRET: 'a'.repeat(32), JWT_REFRESH_SECRET: 'r'.repeat(32) }),
);
const guard = new JwtAuthGuard(new Reflector(), tokenService);

function contextFor(request: AuthenticatedRequest, handler: () => void = () => undefined): ExecutionContext {
  return {
    getHandler: () => handler,
    getClass: () => class TestController {},
    switchToHttp: () => ({ getRequest: () => request }),
  } as unknown as ExecutionContext;
}

function requestWith(authorization?: string): AuthenticatedRequest {
  return { headers: { authorization } } as AuthenticatedRequest;
}

describe('JwtAuthGuard', () => {
  it('lets a @Public() route through without a token', () => {
    const handler = () => undefined;
    Public()(handler);

    expect(guard.canActivate(contextFor(requestWith(), handler))).toBe(true);
  });

  it('puts the token owner on request.user', () => {
    const token = tokenService.signAccessToken({ sub: 'user-1', email: 'ana@example.com', role: ERole.ADMIN });
    const request = requestWith(`Bearer ${token}`);

    guard.canActivate(contextFor(request));

    expect(request.user).toEqual({ id: 'user-1', email: 'ana@example.com', role: ERole.ADMIN });
  });

  it('rejects a request without the Authorization header', () => {
    expect(() => guard.canActivate(contextFor(requestWith()))).toThrow(UnauthorizedException);
  });

  it('rejects a scheme other than Bearer', () => {
    const token = tokenService.signAccessToken({ sub: 'user-1', email: 'ana@example.com', role: ERole.USER });

    expect(() => guard.canActivate(contextFor(requestWith(`Basic ${token}`)))).toThrow(UnauthorizedException);
  });
});
