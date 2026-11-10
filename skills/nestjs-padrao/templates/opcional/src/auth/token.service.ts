import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService, JwtSignOptions } from '@nestjs/jwt';
import { createHash, randomBytes, randomUUID } from 'crypto';
import { DEFAULT_ACCESS_EXPIRES_IN, DEFAULT_REFRESH_EXPIRES_IN, MIN_SECRET_LENGTH } from './auth.constants';
import { ERole } from './enums/role.enum';
import { IAccessTokenPayload, IRefreshTokenPayload } from './interfaces/token-payload.interface';

const ROLES: string[] = Object.values(ERole);

@Injectable()
export class TokenService implements OnModuleInit {
  constructor(
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {}

  // Falha na subida do app em vez de assinar tokens com segredo ausente ou fraco.
  onModuleInit(): void {
    const access = this.requireSecret('JWT_ACCESS_SECRET');
    const refresh = this.requireSecret('JWT_REFRESH_SECRET');
    if (access === refresh) throw new Error('JWT_ACCESS_SECRET and JWT_REFRESH_SECRET must be different');
  }

  signAccessToken(payload: IAccessTokenPayload): string {
    return this.jwtService.sign(payload, {
      secret: this.requireSecret('JWT_ACCESS_SECRET'),
      expiresIn: this.expiresIn('JWT_ACCESS_EXPIRES_IN', DEFAULT_ACCESS_EXPIRES_IN),
    });
  }

  // O jti garante que dois refresh tokens emitidos no mesmo segundo sejam diferentes; sem ele a rotação
  // devolveria o mesmo token e o antigo não seria realmente invalidado.
  signRefreshToken(payload: IRefreshTokenPayload): string {
    return this.jwtService.sign(payload, {
      secret: this.requireSecret('JWT_REFRESH_SECRET'),
      expiresIn: this.expiresIn('JWT_REFRESH_EXPIRES_IN', DEFAULT_REFRESH_EXPIRES_IN),
      jwtid: randomUUID(),
    });
  }

  // Devolve null para qualquer token inválido (assinatura, expirado, formato, papel desconhecido ou refresh trocado).
  verifyAccessToken(token: string): IAccessTokenPayload | null {
    const secret = this.requireSecret('JWT_ACCESS_SECRET');
    try {
      const { sub, email, role } = this.jwtService.verify<Partial<IAccessTokenPayload>>(token, { secret });
      if (typeof sub !== 'string' || typeof email !== 'string' || !role || !ROLES.includes(role)) return null;
      return { sub, email, role };
    } catch {
      return null;
    }
  }

  // Devolve null para qualquer token inválido (assinatura, expirado, formato ou access token trocado).
  verifyRefreshToken(token: string): IRefreshTokenPayload | null {
    const secret = this.requireSecret('JWT_REFRESH_SECRET');
    try {
      const { sub } = this.jwtService.verify<Partial<IRefreshTokenPayload>>(token, { secret });
      return typeof sub === 'string' ? { sub } : null;
    } catch {
      return null;
    }
  }

  // Token opaco de uso único (links de e-mail): 256 bits aleatórios, sem dados dentro. Só o hash vai para o
  // banco; o valor devolvido aqui só existe no e-mail enviado ao usuário.
  generateOpaqueToken(): string {
    return randomBytes(32).toString('base64url');
  }

  // SHA-256 e não bcrypt: o bcrypt só olha os primeiros 72 bytes, e o início de dois JWTs é quase igual.
  // Também serve aos tokens opacos, que já têm entropia alta e por isso não precisam de hash lento.
  hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  private requireSecret(key: string): string {
    const secret = this.configService.get<string>(key);
    if (!secret || secret.length < MIN_SECRET_LENGTH) {
      throw new Error(`${key} must be set and have at least ${MIN_SECRET_LENGTH} characters`);
    }
    return secret;
  }

  private expiresIn(key: string, fallback: string): JwtSignOptions['expiresIn'] {
    return (this.configService.get<string>(key) ?? fallback) as JwtSignOptions['expiresIn'];
  }
}
