import csv
import socket

input_csv = "nslookup.csv"
output_csv = "resolved_ips.csv"

with open(input_csv, mode="r", newline="", encoding="utf-8") as infile, open(output_csv, mode="w", newline="", encoding="utf-8") as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ["Domain", "Port", "IPv4_Addresses"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:
        domain = row["Domain"].strip()
        port = row["Port"].strip()

        try:
            ip_list = list(set(
                info[4][0] for info in socket.getaddrinfo(domain, None, socket.AF_INET)
            ))
            ip_addresses = ", ".join(ip_list) if ip_list else "No IPv4 Found"
        except socket.gaierror:
            ip_addresses = "Resolution Failed"

        writer.writerow({"Domain": domain, "Port": port, "IPv4_Addresses": ip_addresses})

print(f"Resolved IPv4 addresses saved to {output_csv}")
