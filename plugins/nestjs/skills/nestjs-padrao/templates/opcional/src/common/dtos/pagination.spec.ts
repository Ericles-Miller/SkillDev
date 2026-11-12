import { plainToInstance } from 'class-transformer';
import { validateSync } from 'class-validator';
import { PaginatedResponseDto } from './paginated-response.dto';
import { PaginationRequestDto } from './pagination-request.dto';

function parseQuery(query: Record<string, string>): PaginationRequestDto {
  return plainToInstance(PaginationRequestDto, query);
}

describe('PaginationRequestDto', () => {
  it('defaults to page 1 with 10 items when the query is empty', () => {
    expect(parseQuery({})).toMatchObject({ page: 1, limit: 10 });
  });

  it('converts query strings to numbers', () => {
    expect(parseQuery({ page: '3', limit: '25' })).toMatchObject({ page: 3, limit: 25 });
  });

  it('rejects a limit above 100', () => {
    const errors = validateSync(parseQuery({ limit: '101' }));

    expect(errors.map((error) => error.property)).toEqual(['limit']);
  });

  it('rejects page 0', () => {
    const errors = validateSync(parseQuery({ page: '0' }));

    expect(errors.map((error) => error.property)).toEqual(['page']);
  });
});

describe('PaginatedResponseDto.of', () => {
  it('rounds the page count up', () => {
    const response = PaginatedResponseDto.of(['a', 'b'], 21, parseQuery({ page: '3', limit: '10' }));

    expect(response).toMatchObject({ data: ['a', 'b'], total: 21, page: 3, limit: 10, totalPages: 3 });
  });

  it('reports zero pages for an empty result', () => {
    expect(PaginatedResponseDto.of([], 0, parseQuery({})).totalPages).toBe(0);
  });
});
