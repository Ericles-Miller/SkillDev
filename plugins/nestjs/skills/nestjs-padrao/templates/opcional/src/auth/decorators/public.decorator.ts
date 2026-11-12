import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';

// O guard de JWT é global e nega por padrão; @Public() libera uma rota ou um controller inteiro.
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
