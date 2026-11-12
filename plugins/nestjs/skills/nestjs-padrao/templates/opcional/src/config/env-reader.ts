import { ConfigService } from '@nestjs/config';

export interface IEnvReader {
  optional: (name: string) => string | undefined;
  // Falha na subida do app se a variável faltar; `reason` completa a mensagem ("X is required <reason>").
  required: (name: string, reason: string) => string;
}

// Variável vazia ou só com espaços conta como ausente.
export function createEnvReader(configService: ConfigService): IEnvReader {
  const optional = (name: string): string | undefined => configService.get<string>(name)?.trim() || undefined;
  const required = (name: string, reason: string): string => {
    const value = optional(name);
    if (!value) throw new Error(`${name} is required ${reason}`);
    return value;
  };
  return { optional, required };
}
