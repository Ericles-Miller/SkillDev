import { ConfigService } from '@nestjs/config';
import { createEnvReader } from './env-reader';

const env = createEnvReader(new ConfigService({ MAIL_HOST: ' smtp.example.com ', MAIL_FROM: '   ' }));

describe('createEnvReader', () => {
  it('returns the value without surrounding spaces', () => {
    expect(env.optional('MAIL_HOST')).toBe('smtp.example.com');
  });

  it('treats a blank value as missing', () => {
    expect(env.optional('MAIL_FROM')).toBeUndefined();
  });

  it('fails with the variable name and the reason when a required variable is missing', () => {
    expect(() => env.required('MAIL_FROM', 'to send emails')).toThrow('MAIL_FROM is required to send emails');
  });
});
