# Neckermann Nordic - Pricematch Integration Estimation

**Request Date:** 17/06/2026  
**Estimation PIC:** @Raja Fathurrahman  
**Status:** Dev Complete  
**Estimation Type:** Normal

---

## 1. Overview

### Company Information
| Field | Details |
|-------|---------|
| **Company Name** | Corendon |
| **Website** | Neckermann Nordic - Find travel solutions to Turkey, Greece, Egypt and Spain |
| **Industry** | Holiday Package Provider |
| **Integration** | Pricematch Solution |

### Project Scope
- **Frequency:** Daily scraping
- **Delivery Method:** SFTP
- **Key Metrics:** Same as existing Pricematch
- **Matching:** Same method as existing Pricematch
- **Ranking:** No

---

## 2. Website Analysis

### 2.1 Technical Architecture

| Aspect | Details | Complexity |
|--------|---------|------------|
| **Platform** | Next.js (React Server Components) | Medium |
| **Data Loading** | Dynamic via API + Client-side hydration | Medium |
| **API Endpoint** | `https://neckermann-nordic.dk/api/search` | Low |
| **Authentication** | Session-based (cookies required) | Medium |
| **Rate Limiting** | Present but not aggressive | Low |
| **Anti-bot** | Basic headers/cookies check | Low |
| **Data Format** | JSON API response | Low |

### 2.2 API Parameters Analysis

**Endpoint:** `GET https://neckermann-nordic.dk/api/search`

**Required Parameters:**
```
CHARTER=True
ADULT=2
CHECKIN_BEG=YYYYMMDD
CHECKIN_END=YYYYMMDD
CHILD=0
CURRENCY=4
FILTER=1
FREIGHT=1
PARTITION_PRICE=32
PRICE_PAGE=1
RECONPAGE=10
REGULAR=True
SEARCH_MODE=b2c
SEARCH_TYPE=PACKET_TOUR
SORT_TYPE=0
STATE=9 (Turkey)
THE_BEST_AT_TOP=true
TOWNFROM=1941 (CPH) / 1962 (AAL) / 1964 (BLL)
NIGHTMIN=7
NIGHTMAX=7
TOURTYPE=-1
xdebug=true
```

**Optional Filters:**
```
HOTELLIST=
STARLIST=
MEALLIST=
HOTELATTR=
REGIONTO=
TOWNTO=
COSTMIN=
COSTMAX=
```

### 2.3 Response Structure

```json
[
  {
    "state": {
      "inc": 9,
      "name": "TURKEY",
      "lname": "TURKEY"
    },
    "prices": [
      {
        "hotelName": "Hotel Name",
        "hotelLName": "Hotel Name",
        "starName": "***",
        "mealName": "AI",
        "roomName": "STANDARD ROOM",
        "htPlaceName": "DBL",
        "price": 1039.77,
        "priceOld": 1261.77,
        "checkIn": "2026-06-26T00:00:00",
        "checkOut": "2026-07-03T00:00:00",
        "nights": 7,
        "pages": 19,
        "hotelInc": 1048,
        "townInc": "1943",
        "starInc": 3,
        "economIn": 2,
        "economOut": 2,
        "spog": 287561,
        "cat_Claim": "...",
        "cat_Claim_Inc": 2411473
      }
    ]
  }
]
```

---

## 3. Scraping Effort Estimation

### 3.1 Website Traffic Estimation

| Metric | Estimate | Notes |
|--------|----------|-------|
| **Daily Page Views** | ~50,000 - 100,000 | Holiday package provider |
| **Concurrent Users** | ~500 - 1,000 | Seasonal variation |
| **API Call Frequency** | ~10,000/day | Search queries |

### 3.2 Request & Traffic Estimation

**Per Day Calculation:**

| Parameter | Value | Calculation |
|-------------|-------|-------------|
| **Destinations** | 4 | Turkey, Greece, Egypt, Spain |
| **Departures** | 3 | AAL, CPH, BLL |
| **Date Checks** | 52 | 365 days / 7-day intervals |
| **Pages per Date** | 1-20 | Average ~5 |
| **Total Requests/Day** | ~3,120 | 4 × 3 × 52 × 5 |
| **Request Size** | ~500 bytes | Headers + params |
| **Response Size** | ~50 KB | Average JSON response |
| **Total Data/Day** | ~156 MB | 3,120 × 50 KB |
| **Proxy Traffic/Day** | ~200-250 MB | With overhead |
| **Proxy Traffic/Month** | ~6-7.5 GB | |

### 3.3 Difficulty Assessment

| Aspect | Level | Weeks | Notes |
|--------|-------|-------|-------|
| **API Understanding** | Low | 0.5 | Well-documented JSON API |
| **Authentication** | Medium | 1 | Cookie/session management |
| **Rate Limiting** | Low | 0.5 | Basic throttling |
| **Data Parsing** | Low | 0.5 | Structured JSON |
| **Error Handling** | Medium | 1 | Session expiry, retries |
| **Pagination** | Low | 0.5 | Page-based (PRICE_PAGE) |
| **Dynamic Content** | Low | 0.5 | API-based, not browser |
| **Testing** | Medium | 1 | Multi-departure, date ranges |
| **Documentation** | Low | 0.5 | Clear API structure |
| **Total Development** | | **6 weeks** | 4-6 weeks realistic |

---

## 4. Integration Estimation

### 4.1 Add to Matching Flow

| Task | Estimated Days | Notes |
|------|---------------|-------|
| **API Client Development** | 2 days | Build robust API client |
| **Data Parser** | 1 day | Map to Pricematch schema |
| **Hotel Matching Logic** | 2 days | Hotel name, location, stars |
| **Price Matching Logic** | 1 day | Room type, meal plan, dates |
| **Testing & Validation** | 2 days | End-to-end testing |
| **Total** | **8 days** | ~1.5 weeks |

### 4.2 Add to Scheduling

| Task | Estimated Days | Notes |
|------|---------------|-------|
| **Scheduler Configuration** | 1 day | Daily cron setup |
| **Queue Management** | 1 day | Multi-departure queuing |
| **Monitoring Setup** | 1 day | Alerts, health checks |
| **Retry Logic** | 1 day | Failed request handling |
| **Total** | **4 days** | ~1 week |

### 4.3 Data Pipeline

| Task | Estimated Days | Notes |
|------|---------------|-------|
| **SFTP Export** | 1 day | File generation and upload |
| **Data Validation** | 1 day | Schema validation |
| **Error Reporting** | 1 day | Failure notifications |
| **Total** | **3 days** | ~0.5 week |

---

## 5. Proxy Usage Estimation

### 5.1 Daily Proxy Traffic

| Scenario | GB/Day | Notes |
|----------|--------|-------|
| **Minimal (1 destination)** | ~50 MB | Turkey only |
| **Standard (4 destinations)** | ~200 MB | All destinations |
| **Full (all params)** | ~300 MB | All meal plans, stars |
| **With retry overhead** | ~400 MB | 33% retry buffer |

### 5.2 Monthly Proxy Traffic

| Scenario | GB/Month | Cost Estimate* |
|----------|----------|----------------|
| **Minimal** | ~1.5 GB | Low |
| **Standard** | ~6 GB | Medium |
| **Full** | ~9 GB | Medium |
| **With overhead** | ~12 GB | Medium-High |

*Cost depends on proxy provider rates

### 5.3 Proxy Recommendations

| Type | Recommendation | Reason |
|------|---------------|--------|
| **Residential** | Not required | No aggressive bot detection |
| **Datacenter** | Sufficient | Basic API scraping |
| **Rotation** | Recommended | Avoid rate limits |
| **Location** | Denmark/EU | Target website location |

---

## 6. Total Effort Summary

### 6.1 Development Timeline

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| **Requirements & Setup** | 1 week | Week 1 | Week 1 |
| **Core Scraper Development** | 2 weeks | Week 2 | Week 3 |
| **Integration & Matching** | 2 weeks | Week 4 | Week 5 |
| **Testing & QA** | 1 week | Week 6 | Week 6 |
| **Deployment & Monitoring** | 1 week | Week 7 | Week 7 |
| **Total** | **7 weeks** | | |

### 6.2 Resource Allocation

| Role | Effort | Notes |
|------|--------|-------|
| **Backend Developer** | 4 weeks | API client, parser, scheduler |
| **Integration Developer** | 2 weeks | Matching flow, data pipeline |
| **QA Engineer** | 1 week | Testing, validation |
| **DevOps** | 0.5 week | Deployment, monitoring |
| **Total** | **7.5 weeks** | |

### 6.3 Risk Factors

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **API Changes** | Medium | High | Monitor API, version pinning |
| **Rate Limiting** | Low | Medium | Proxy rotation, throttling |
| **Session Expiry** | Medium | Medium | Auto-refresh cookies |
| **Data Volume** | Low | Medium | Incremental scraping |
| **Seasonal Variation** | High | Low | Adjust frequency |

---

## 7. Implementation Notes

### 7.1 Key Findings from POC

1. **API is Accessible**: The `/api/search` endpoint returns structured JSON
2. **Session Required**: Cookies needed for authentication
3. **Pagination**: Uses `PRICE_PAGE` parameter (1-20 pages typical)
4. **Date Range**: Check-in dates in `YYYYMMDD` format
5. **Multi-Departure**: Supports AAL (1962), CPH (1941), BLL (1964)
6. **Response Size**: ~50 KB per page, ~10 hotels per page

### 7.2 Recommended Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Scheduler     │────▶│  API Client     │────▶│  Data Parser    │
│   (Daily Cron)    │     │  (Neckermann)   │     │  (JSON → CSV)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Matching Engine │
                                               │  (Pricematch)   │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  SFTP Export    │
                                               │  (Delivery)     │
                                               └─────────────────┘
```

### 7.3 Sample Scraper Output

```json
{
  "hotels": [
    {
      "name": "Mitos Apart Hotel",
      "star_rating": "***",
      "meal_plan": "RO",
      "room_type": "STANDARD ROOM",
      "price": 840.00,
      "original_price": 840.00,
      "check_in": "2026-06-25T00:00:00",
      "check_out": "2026-07-02T00:00:00",
      "nights": 7,
      "departure": "AAL",
      "hotel_inc": 1048,
      "town_inc": "1943"
    }
  ],
  "total": 520,
  "parameters": {
    "departures": ["AAL", "CPH", "BLL"],
    "nights": 7,
    "days_range": 365
  }
}
```

---

## 8. Next Steps

### 8.1 Immediate Actions

- [ ] Review and approve estimation
- [ ] Assign development team
- [ ] Set up proxy infrastructure
- [ ] Create development environment
- [ ] Schedule kickoff meeting

### 8.2 Development Milestones

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| **M1: API Client** | Week 2 | Working API scraper |
| **M2: Data Parser** | Week 3 | Structured data output |
| **M3: Matching** | Week 5 | Integrated with Pricematch |
| **M4: Testing** | Week 6 | QA sign-off |
| **M5: Production** | Week 7 | Live deployment |

### 8.3 Questions for Client

1. **Scope Confirmation**: Turkey only or all 4 destinations (Turkey, Greece, Egypt, Spain)?
2. **Frequency**: Daily at what time? (e.g., 2 AM local time)
3. **Data Retention**: How long to keep historical data?
4. **Alert Thresholds**: What constitutes a scraping failure?
5. **Proxy Budget**: Monthly proxy budget limit?

---

## 9. Conclusion

**Total Estimated Effort: 6-7 weeks**

**Breakdown:**
- Scraper Development: 4 weeks
- Integration: 2 weeks
- Testing & Deployment: 1 week

**Proxy Usage: ~200-400 MB/day (~6-12 GB/month)**

**Risk Level: Low-Medium**

The Neckermann Nordic API is well-structured and accessible. The main complexity lies in session management and handling the volume of requests across multiple departures and date ranges. With proper proxy rotation and rate limiting, this should be a straightforward integration.

---

*Document Version: 1.0*  
*Last Updated: 2026-06-22*  
*Author: Raja Fathurrahman*
