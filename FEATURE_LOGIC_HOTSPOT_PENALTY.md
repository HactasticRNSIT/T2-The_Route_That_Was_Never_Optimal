# Hotspot Verification, Clearance, and Truck Penalty Logic

## Citizen report verification
1. Citizen submits a report from the user page.
2. Admin opens **Citizen Reports**.
3. The admin now sees full report details: citizen name, coordinates, address, landmark, geotag source, camera verification, detected fill level, description, generated hotspot ID, admin remarks, and lifecycle status.
4. When admin clicks **Verify**, the backend checks:
   - If the same hotspot is already active nearby, it links the report to the existing hotspot and avoids duplicate map markers.
   - If the same hotspot was previously cleared by a truck simulation, it creates a new hotspot and creates a truck penalty.
   - Otherwise, it creates a normal active hotspot.

## Truck simulation clearance
1. Admin runs optimization.
2. Admin starts a truck route from Route Plan or Trucks.
3. When the truck simulation reaches the end, the backend marks every hotspot stop on that truck route as `collected`.
4. Collected hotspots are removed from the dashboard map and removed from the next optimization input.
5. The original hotspot record is kept internally with `clearedByTruckId`, `clearedByVehicleNumber`, `clearedAt`, and `clearedViaRouteId` so repeat failures can be audited.

## Repeat hotspot penalty
1. After a truck simulation clears a hotspot, submit the same location again from the user report page.
2. Admin verifies the new report.
3. Backend checks for a previously cleared hotspot within roughly 120 meters.
4. If found, the backend creates a penalty against the truck that cleared it earlier.
5. The penalty appears in the new **Penalties** tab in the admin page.

## Important behavior
- Hotspots disappear from the map only after a truck route simulation is completed.
- A report becoming verified creates/re-activates a hotspot.
- Running optimization after clearance excludes cleared hotspots.
- Running optimization after a repeat verified report includes the new hotspot again and shows the penalty separately.

## Fast Non-Overlapping Micro-Route Update

Latest update:
- Increased active fleet from 3 trucks to 8 trucks.
- Each truck now owns exactly one service zone/micro-route.
- Active hotspots are assigned to only one truck, so route stops do not overlap.
- Added nearby micro depots and nearby waste processing points so routes are short and simulations finish quickly.
- Default simulation speed is now 8x, with controls cycling through 8x, 16x, and 32x.
- Backend routing defaults to fast offline demo routing. To use live OSRM road routing, run with `USE_OSRM=true npm start`.

Truck-zone mapping:
- Truck 001: Indiranagar biomedical route
- Truck 002: Koramangala mixed waste route
- Truck 003: HSR organic route
- Truck 004: BTM regular waste route
- Truck 005: Ejipura organic route
- Truck 006: Bellandur dry waste route
- Truck 007: Electronic City e-waste route
- Truck 008: Peenya hazardous route
