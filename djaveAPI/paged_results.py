import math

from djaveAPI.problem import Problem
from djaveAPI.to_json import to_json_dict


PAGE = 'page'
RESULTS = 'results'
PAGING = 'paging'
OBJECT_COUNT = 'object_count'
PAGE_SIZE = 'page_size'
FIRST_PAGE = 'first_page'
ON_PAGE = 'on_page'
TOTAL_PAGES = 'total_pages'


USE_PAGE_SIZE = 100
USE_FIRST_PAGE = 1


def get_page(request_GET):
  if PAGE in request_GET:
    page = request_GET[PAGE]
    if page != '':
      try:
        page = int(page)
      except ValueError:
        raise Problem('I expect page to be an integer')
      if page < USE_FIRST_PAGE:
        raise Problem(
            'The page should be greater than or equal to {}'.format(
                USE_FIRST_PAGE))
      return page


def paged_results(model, query, page):
  count = query.count()
  total_pages = math.ceil(1.0 * count / USE_PAGE_SIZE)
  page = page or USE_FIRST_PAGE
  results = []
  from_row = (page - 1) * USE_PAGE_SIZE
  to_row = page * USE_PAGE_SIZE
  for obj in query.order_by('pk')[from_row:to_row]:
    results.append(to_json_dict(obj, model))
  return construct_paged_results(results, count, page, total_pages)


def construct_paged_results(results, count, page, total_pages):
  return {
      RESULTS: results,
      PAGING: {
          OBJECT_COUNT: count,
          PAGE_SIZE: USE_PAGE_SIZE,
          FIRST_PAGE: USE_FIRST_PAGE,
          ON_PAGE: page,
          TOTAL_PAGES: total_pages}}
