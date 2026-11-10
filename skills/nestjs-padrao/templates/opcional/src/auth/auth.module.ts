import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { JwtModule } from '@nestjs/jwt';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import { RolesGuard } from './guards/roles.guard';
import { TokenService } from './token.service';

@Module({
  // Sem segredo padrão: cada assinatura escolhe o segredo (acesso ou refresh) no TokenService.
  imports: [JwtModule.register({})],
  providers: [
    TokenService,
    // Global e negando por padrão: rota nova nasce protegida, e só @Public() a libera.
    { provide: APP_GUARD, useClass: JwtAuthGuard },
    // Registrado depois do JwtAuthGuard para rodar depois dele, quando request.user já existe.
    { provide: APP_GUARD, useClass: RolesGuard },
  ],
  exports: [TokenService],
})
export class AuthModule {}
