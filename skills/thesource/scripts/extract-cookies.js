async (page) => {
  const cookies = await page.context().cookies();
  return cookies
    .filter(c => c.domain.includes('source.redhat.com') && c.httpOnly)
    .map(c => `${c.name}=${c.value}`)
    .join('; ');
}
