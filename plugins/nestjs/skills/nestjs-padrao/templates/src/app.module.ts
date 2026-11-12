import { ClassSerializerInterceptor, Module, ValidationPipe } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { APP_INTERCEPTOR, APP_PIPE } from '@nestjs/core';
import { HealthController } from './health.controller';

@Module({
  imports: [ConfigModule.forRoot({ isGlobal: true })],
  controllers: [HealthController],
  providers: [
    {
      // Pipe global registrado como provider (e não no main.ts) para valer também nos testes.
      // whitelist + forbidNonWhitelisted: campo que o DTO não declara é recusado, e não ignorado.
      provide: APP_PIPE,
      useValue: new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }),
    },
    // Sem ele, o @Exclude() das entidades não age e a senha ou o hash do token sai na resposta.
    { provide: APP_INTERCEPTOR, useClass: ClassSerializerInterceptor },
  ],
})
export class AppModule {}
