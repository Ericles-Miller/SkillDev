import { ApiProperty } from '@nestjs/swagger';
import { PaginationRequestDto } from './pagination-request.dto';

// O genérico não aparece no Swagger: cada listagem declara <Entidade>PageResponseDto estendendo esta classe
// e redeclarando `data` com @ApiProperty({ type: [<Entidade>ResponseDto] }).
export class PaginatedResponseDto<T> {
  data: T[];

  @ApiProperty({ description: 'Total number of items across all pages', example: 42 })
  total: number;

  @ApiProperty({ description: 'Current page number', example: 1 })
  page: number;

  @ApiProperty({ description: 'Items per page', example: 10 })
  limit: number;

  @ApiProperty({ description: 'Total number of pages', example: 5 })
  totalPages: number;

  static of<T>(data: T[], total: number, { page, limit }: PaginationRequestDto): PaginatedResponseDto<T> {
    const response = new PaginatedResponseDto<T>();
    response.data = data;
    response.total = total;
    response.page = page;
    response.limit = limit;
    response.totalPages = Math.ceil(total / limit);
    return response;
  }
}
