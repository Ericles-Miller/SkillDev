import { CanActivate, ExecutionContext, Injectable, UnauthorizedException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { IS_PUBLIC_KEY } from '../decorators/public.decorator';
import { AuthenticatedRequest } from '../interfaces/authenticated-user.interface';
import { TokenService } from '../token.service';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(
    private readonly reflector: Reflector,
    private readonly tokenService: TokenService,
  ) {}

  canActivate(context: ExecutionContext): boolean {
    const isPublic = this.reflector.getAllAndOverride<boolean | undefined>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const token = this.extractBearerToken(request);
    const payload = token ? this.tokenService.verifyAccessToken(token) : null;
    if (!payload) throw new UnauthorizedException('Invalid or missing access token');

    request.user = { id: payload.sub, email: payload.email, role: payload.role };
    return true;
  }

  private extractBearerToken(request: AuthenticatedRequest): string | null {
    const [scheme, token] = (request.headers.authorization ?? '').split(' ');
    return scheme?.toLowerCase() === 'bearer' && token ? token : null;
  }
}
