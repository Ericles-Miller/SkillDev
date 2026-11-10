import { createParamDecorator, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { AuthenticatedRequest, IAuthenticatedUser } from '../interfaces/authenticated-user.interface';

export const CurrentUser = createParamDecorator((_data: unknown, context: ExecutionContext): IAuthenticatedUser => {
  const { user } = context.switchToHttp().getRequest<AuthenticatedRequest>();
  // Só acontece se a rota foi marcada @Public() e mesmo assim pediu o usuário.
  if (!user) throw new UnauthorizedException('Authentication required');
  return user;
});
