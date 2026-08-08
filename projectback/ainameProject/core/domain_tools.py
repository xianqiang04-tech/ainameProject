import asyncio

async def check_domain(domain):
    if not domain.endswith(".com"):
        if "." not in domain:
            domain += ".com"
        else:
            return "仅支持.com校验"

    reader, writer = await asyncio.wait_for(
        asyncio.open_connection('whois.verisign-grs.com',43),
        timeout=3.0,
    )

    writer.write((domain + "\n").encode("utf-8"))
    await writer.drain()

    response = await asyncio.wait_for(reader.read(), timeout=3.0)

    writer.close()
    await writer.wait_closed()

    result = response.decode("utf-8",errors="ignore")

    if "No match for" in result:
        return "✅ 未注册 (可买)"
    else:
        return "❌ 已被抢注"
