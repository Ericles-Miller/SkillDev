import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { ERole } from './enums/role.enum';
import { TokenService } from './token.service';

const ACCESS_SECRET = 'a'.repeat(32);
const REFRESH_SECRET = 'r'.repeat(32);

function buildService(env: Record<string, string> = {}): TokenService {
  const config = new ConfigService({ JWT_ACCESS_SECRET: ACCESS_SECRET, JWT_REFRESH_SECRET: REFRESH_SECRET, ...env });
  return new TokenService(new JwtService(), config);
}

describe('TokenService', () => {
  it('verifies an access token back to the payload it was signed with', () => {
    const service = buildService();

    const token = service.signAccessToken({ sub: 'user-1', email: 'ana@example.com', role: ERole.USER });

    expect(service.verifyAccessToken(token)).toEqual({ sub: 'user-1', email: 'ana@example.com', role: ERole.USER });
  });

  it('rejects a refresh token presented as an access token', () => {
    const service = buildService();

    const refreshToken = service.signRefreshToken({ sub: 'user-1' });

    expect(service.verifyAccessToken(refreshToken)).toBeNull();
  });

  it('rejects an access token whose role is not in ERole', () => {
    const service = buildService();
    const token = new JwtService().sign(
      { sub: 'user-1', email: 'ana@example.com', role: 'root' },
      { secret: ACCESS_SECRET },
    );

    expect(service.verifyAccessToken(token)).toBeNull();
  });

  it('issues a different refresh token on every call, even within the same second', () => {
    const service = buildService();

    expect(service.signRefreshToken({ sub: 'user-1' })).not.toBe(service.signRefreshToken({ sub: 'user-1' }));
  });

  it('refuses to start with a secret shorter than 32 characters', () => {
    const service = buildService({ JWT_ACCESS_SECRET: 'short' });

    expect(() => service.onModuleInit()).toThrow('JWT_ACCESS_SECRET must be set and have at least 32 characters');
  });

  it('refuses to start when access and refresh secrets are equal', () => {
    const service = buildService({ JWT_REFRESH_SECRET: ACCESS_SECRET });

    expect(() => service.onModuleInit()).toThrow('JWT_ACCESS_SECRET and JWT_REFRESH_SECRET must be different');
  });

  it('hashes a token with SHA-256', () => {
    expect(buildService().hashToken('abc')).toBe('ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  });
});
