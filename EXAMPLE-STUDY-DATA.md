# Study collection data example
Data privacy especially in ones home is extremely personal and important.
We do not want to collect any personal data from this study at all and have gone to great lengths to ensure we do not receive any of your personal data.

The data below was collected from a live system and represents the data we wish to collect from your system.
All personal data has been entirely removed from the collection dataset, we are using a collection of pseudonymization, aggregation and stripping methods to entirely remove any traces of personally identifiable information from the original dataset.
We were also careful to ensure no de-anonymization of the hashed data would be possible by using a unique salt to your computer which we are not collecting and have no way of knowing.
Our methods for collecting this data are all in this automation: [collect_system_metrics.py](collect_system_metrics.py)

Please read through each of these carefully.
If you have any questions or concerns about any of these metrics or the collection methods we have enabled to perform our anonymization please let us know.

### em_1_asset_register table

|    | created_at   |   count | added_on            |
|---:|:-------------|--------:|:--------------------|
|  0 | 2024-01-23   |       9 | 2024-01-23 01:48:43 |
|  1 | 2024-01-14   |       8 | 2024-01-23 01:48:43 |

### em_1_named_asset_register table

|    | created_at   |   count | added_on            |
|---:|:-------------|--------:|:--------------------|
|  0 | 2024-01-20   |       3 | 2024-01-23 01:48:43 |
|  1 | 2024-01-23   |       2 | 2024-01-23 01:48:43 |

### em_2_software_register table

|    |   installed |   decommissioned |   updated | added_on            |
|---:|------------:|-----------------:|----------:|:--------------------|
|  0 |         115 |                9 |        39 | 2024-01-23 02:05:30 |
|  1 |         115 |                9 |        39 | 2024-01-23 03:07:47 |
|  2 |         115 |                9 |        39 | 2024-01-24 02:05:33 |
|  3 |         115 |                9 |        39 | 2024-01-25 01:31:47 |

### em_3_firewall_rules table

|    |   enabled |   disabled | added_on            |
|---:|----------:|-----------:|:--------------------|
|  0 |       477 |        287 | 2024-01-23 02:56:03 |
|  1 |       477 |        287 | 2024-01-23 03:07:47 |
|  2 |       477 |        287 | 2024-01-24 02:05:33 |
|  3 |       477 |        287 | 2024-01-25 01:31:47 |

### em_4_scheduled_tasks table

|    |   enabled |   disabled | added_on            |
|---:|----------:|-----------:|:--------------------|
|  0 |       156 |         31 | 2024-01-23 03:04:22 |
|  1 |       156 |         31 | 2024-01-23 03:06:24 |
|  2 |       156 |         31 | 2024-01-23 03:07:47 |
|  3 |       156 |         31 | 2024-01-24 02:05:33 |
|  4 |       156 |         31 | 2024-01-25 01:31:47 |

### em_5_enabled_services table

|    |   Manual |   Automatic |   Disabled | added_on            |
|---:|---------:|------------:|-----------:|:--------------------|
|  0 |      201 |          83 |         12 | 2024-01-23 03:25:27 |
|  1 |      201 |          83 |         12 | 2024-01-23 03:25:35 |
|  2 |      201 |          83 |         12 | 2024-01-24 02:05:33 |
|  3 |      201 |          83 |         12 | 2024-01-25 01:31:47 |

### em_6_defender_updates table

|    |   AMServiceEnabled |   AntispywareEnabled |   AntivirusEnabled |   BehaviorMonitorEnabled |   DefenderSignaturesOutOfDate |   FullScanAge |   FullScanRequired |   IoavProtectionEnabled |   IsTamperProtected |   NISEnabled |   OnAccessProtectionEnabled |   QuickScanOverdue |   RealTimeProtectionEnabled | created_at          | added_on            |
|---:|-------------------:|---------------------:|-------------------:|-------------------------:|------------------------------:|--------------:|-------------------:|------------------------:|--------------------:|-------------:|----------------------------:|-------------------:|----------------------------:|:--------------------|:--------------------|
|  0 |                  1 |                    1 |                  1 |                        1 |                             0 |    4294967295 |                  0 |                       1 |                   1 |            1 |                           1 |                  0 |                           1 | 2024-01-20 23:55:47 | 2024-01-23 23:31:32 |
|  1 |                  1 |                    1 |                  1 |                        1 |                             0 |    4294967295 |                  0 |                       1 |                   1 |            1 |                           1 |                  0 |                           1 | 2024-01-20 23:55:47 | 2024-01-24 02:05:33 |
|  2 |                  1 |                    1 |                  1 |                        1 |                             0 |    4294967295 |                  0 |                       1 |                   1 |            1 |                           1 |                  0 |                           1 | 2024-01-20 23:55:47 | 2024-01-25 01:31:47 |

### em_7_password_policy table

|    |   MinimumPasswordAge |   MaximumPasswordAge |   MinimumPasswordLength |   PasswordComplexity |   PasswordHistorySize |   LockoutBadCount |   RequireLogonToChangePassword |   ForceLogoffWhenHourExpire |   EnableAdminAccount |   EnableGuestAccount | created_at          | added_on            |
|---:|---------------------:|---------------------:|------------------------:|---------------------:|----------------------:|------------------:|-------------------------------:|----------------------------:|---------------------:|---------------------:|:--------------------|:--------------------|
|  0 |                    0 |                   -1 |                       0 |                    1 |                     0 |                 0 |                              0 |                           0 |                    0 |                    0 | 2024-01-06 15:57:13 | 2024-01-23 23:39:47 |
|  1 |                    0 |                   -1 |                       0 |                    1 |                     0 |                 0 |                              0 |                           0 |                    0 |                    0 | 2024-01-06 15:57:13 | 2024-01-24 02:05:33 |
|  2 |                    0 |                   -1 |                       0 |                    1 |                     0 |                 0 |                              0 |                           0 |                    0 |                    0 | 2024-01-06 15:57:13 | 2024-01-25 01:31:47 |

### em_8_wlan_settings table

|    | SSIDHash                                                         | Authentication   | Cipher   | PasswordStrength   | created_at          | added_on            |
|---:|:-----------------------------------------------------------------|:-----------------|:---------|:-------------------|:--------------------|:--------------------|
|  0 | cbbe4a0408d9d1c1116a23f786eb3d3c9b541549b4d09df39a54520dcf673729 | WPA2-Personal    | GCMP     | Strongest          | 2024-01-06 16:40:05 | 2024-01-23 23:55:00 |
|  1 | 8659b9f8ed917593f821f901b2876bcec956f081bd822d8481b1af1afcf882f9 | WPA2-Personal    | GCMP     | Strongest          | 2024-01-06 16:40:05 | 2024-01-23 23:55:00 |
|  2 | cb207ebf1347ffb81a174a299651a2152db8fb6ac117bd589777ea7346bfc445 | WPA2-Personal    | GCMP     | Medium             | 2024-01-06 16:40:05 | 2024-01-23 23:55:00 |
|  3 | 324e9a5a3673feae044e3248432e76d6ce5fff6866e797464e514aaeb5522f2e | WPA2-Personal    | GCMP     | Medium             | 2024-01-06 16:40:05 | 2024-01-23 23:55:00 |
|  4 | 8ae7e4a3a27e8ea1c06ea9f4ae6771f59e8608aadedf37c8dd81badca2218681 | WPA2-Personal    | GCMP     | Strongest          | 2024-01-06 16:40:05 | 2024-01-23 23:55:00 |
|  5 | cac86d7445140659849e53544f71505d8666807af3570d3b57af3275115bb8de | WPA2-Personal    | GCMP     | Strong             | 2024-01-06 16:40:05 | 2024-01-23 23:55:00 |
|  6 | 90a47b4a2363372b48d6f6fb0094ff7fdfcdc1b891ddf9aa2e09a1edd38535a6 | WPA2-Personal    | GCMP     | Strongest          | 2024-01-06 16:40:05 | 2024-01-25 01:31:47 |
|  7 | f07e4915ddbca959f0c09f0df7dd5c68d1ebde83c7e689ddfa567697813eae20 | WPA2-Personal    | GCMP     | Strongest          | 2024-01-06 16:40:05 | 2024-01-25 01:31:47 |
|  8 | 7a05c657699ae098b0a9e781bb23c66365f1b649ccaeb8e2f18fb7bb4229983a | WPA2-Personal    | GCMP     | Medium             | 2024-01-06 16:40:05 | 2024-01-25 01:31:47 |
|  9 | b674e5ef365e3cb662caf0b4c1eacdd5038d97927a6b98980a15701684ff4efb | WPA2-Personal    | GCMP     | Medium             | 2024-01-06 16:40:05 | 2024-01-25 01:31:47 |
| 10 | ce3fb37047b84a65235594c393f0a757e604caa13dedeb42c860224ea092a883 | WPA2-Personal    | GCMP     | Strongest          | 2024-01-06 16:40:05 | 2024-01-25 01:31:47 |

### em_9_controlled_folder_access table

|    |   EnableControlledFolderAccess | created_at          | added_on            |
|---:|-------------------------------:|:--------------------|:--------------------|
|  0 |                              1 | 2024-01-06 18:05:13 | 2024-01-24 00:52:20 |
|  1 |                              1 | 2024-01-06 18:05:13 | 2024-01-24 02:05:33 |
|  2 |                              1 | 2024-01-06 18:05:13 | 2024-01-25 01:31:47 |

### em_10_onedrive_enabled table

|    | AccountName                                                      | KfmFoldersProtectedNow   |   LastKnownFolderBackupTime | created_at          | added_on            |
|---:|:-----------------------------------------------------------------|:-------------------------|----------------------------:|:--------------------|:--------------------|
|  0 | 8911aa9239cc0d5450a45a64e2432eaf3a765b6ec2f1be10b651ff26b291d6fc |                          |                   000000000 | 2024-01-06 18:09:41 | 2024-01-24 01:13:47 |
|  1 | 8c8ee77d77591028ba4da7b1522c323c5474f31e837d82176fc7c181c4ec8ac5 |                          |                   000000000 | 2024-01-06 18:09:41 | 2024-01-25 01:31:47 |

### em_11_vulnerability_patching table

|    | UpdateGUID                             | Software                                                                                | EventIdentifier   | TimeGenerated             | added_on            |
|---:|:---------------------------------------|:----------------------------------------------------------------------------------------|:------------------|:--------------------------|:--------------------|
|  0 | {091939e1-018b-400c-8708-2085cccaafba} | 2023-12 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5033375) | Installed         | 20231215060522.240996-000 | 2024-01-24 01:28:08 |
|  1 | {091939e1-018b-400c-8708-2085cccaafba} | 2023-12 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5033375) | Install Started   | 20231215015845.777587-000 | 2024-01-24 01:28:08 |
|  2 | {091939e1-018b-400c-8708-2085cccaafba} | 2023-12 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5033375) | Download started  | 20231213011939.543025-000 | 2024-01-24 01:28:08 |
|  3 | {7abb93b7-ad91-4919-929b-783ca004ac0a} | 2023-11 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5032190) | Installed         | 20231117224748.682676-000 | 2024-01-24 01:28:08 |
|  4 | {7abb93b7-ad91-4919-929b-783ca004ac0a} | 2023-11 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5032190) | Install Started   | 20231117021251.558724-000 | 2024-01-24 01:28:08 |
|  5 | {7abb93b7-ad91-4919-929b-783ca004ac0a} | 2023-11 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5032190) | Download started  | 20231115022522.203512-000 | 2024-01-24 01:28:08 |
|  6 | {a86b89c3-c593-4b6f-9be5-da1a081f2307} | 2023-10 Update for Windows 11 Version 22H2 for x64-based Systems (KB4023057)            | Installed         | 20231110035520.136989-000 | 2024-01-24 01:28:08 |
|  7 | {a86b89c3-c593-4b6f-9be5-da1a081f2307} | 2023-10 Update for Windows 11 Version 22H2 for x64-based Systems (KB4023057)            | Install Started   | 20231110035519.324330-000 | 2024-01-24 01:28:08 |
|  8 | {a86b89c3-c593-4b6f-9be5-da1a081f2307} | 2023-10 Update for Windows 11 Version 22H2 for x64-based Systems (KB4023057)            | Download started  | 20231110033236.723228-000 | 2024-01-24 01:28:08 |
|  9 | {84148c89-393a-45bc-a52c-2514cb56f6ae} | 2023-10 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5031354) | Download started  | 20231109010710.359641-000 | 2024-01-24 01:28:08 |
| 10 | {84148c89-393a-45bc-a52c-2514cb56f6ae} | 2023-10 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5031354) | Installed         | 20231013035012.194262-000 | 2024-01-24 01:28:08 |
| 11 | {84148c89-393a-45bc-a52c-2514cb56f6ae} | 2023-10 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5031354) | Install Started   | 20231012170709.373408-000 | 2024-01-24 01:28:08 |
| 12 | {84148c89-393a-45bc-a52c-2514cb56f6ae} | 2023-10 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5031354) | Download started  | 20231011015654.947623-000 | 2024-01-24 01:28:08 |
| 13 | {51b8cbee-1d47-4c9a-9120-f6d98c88125e} | 2023-09 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5030219) | Installed         | 20230915120231.336360-000 | 2024-01-24 01:28:08 |
| 14 | {51b8cbee-1d47-4c9a-9120-f6d98c88125e} | 2023-09 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5030219) | Install Started   | 20230915015147.975043-000 | 2024-01-24 01:28:08 |
| 15 | {51b8cbee-1d47-4c9a-9120-f6d98c88125e} | 2023-09 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5030219) | Download started  | 20230913204935.957446-000 | 2024-01-24 01:28:08 |
| 16 | {66b17e1a-cfad-4ca7-a3d5-f23ee7a57e66} | 2023-08 Update for Windows 11 Version 22H2 for x64-based Systems (KB4023057)            | Install Started   | 20230908115759.751539-000 | 2024-01-24 01:28:08 |
| 17 | {66b17e1a-cfad-4ca7-a3d5-f23ee7a57e66} | 2023-08 Update for Windows 11 Version 22H2 for x64-based Systems (KB4023057)            | Download started  | 20230906115153.791009-000 | 2024-01-24 01:28:08 |
| 18 | {86b7ec71-01dd-4968-98fa-9534cdee9d8a} | 2023-08 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5029263) | Installed         | 20230809025417.459039-000 | 2024-01-24 01:28:08 |
| 19 | {86b7ec71-01dd-4968-98fa-9534cdee9d8a} | 2023-08 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5029263) | Install Started   | 20230809015444.757498-000 | 2024-01-24 01:28:08 |
| 20 | {86b7ec71-01dd-4968-98fa-9534cdee9d8a} | 2023-08 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5029263) | Download started  | 20230808233107.963924-000 | 2024-01-24 01:28:08 |
| 21 | {ce0579a9-5cd8-4ea1-83fd-8f9b79f70106} | 2023-07 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5028185) | Installed         | 20230714010535.801865-000 | 2024-01-24 01:28:08 |
| 22 | {ce0579a9-5cd8-4ea1-83fd-8f9b79f70106} | 2023-07 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5028185) | Install Started   | 20230713120317.860900-000 | 2024-01-24 01:28:08 |
| 23 | {ce0579a9-5cd8-4ea1-83fd-8f9b79f70106} | 2023-07 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5028185) | Download started  | 20230712221634.278050-000 | 2024-01-24 01:28:08 |
| 24 | {00518b25-68ab-4b8f-b853-e38bd4347737} | 2023-06 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5027231) | Installed         | 20230619182114.947147-000 | 2024-01-24 01:28:08 |
| 25 | {00518b25-68ab-4b8f-b853-e38bd4347737} | 2023-06 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5027231) | Install Started   | 20230618235320.667213-000 | 2024-01-24 01:28:08 |
| 26 | {00518b25-68ab-4b8f-b853-e38bd4347737} | 2023-06 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5027231) | Download started  | 20230618234922.105991-000 | 2024-01-24 01:28:08 |
| 27 | {7d2c9b43-ed1e-453a-8f90-3cde5808d99d} | 2023-05 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5026372) | Installed         | 20230512214355.854300-000 | 2024-01-24 01:28:08 |
| 28 | {f44ea661-292a-45af-aeda-94a33429e09c} | 2023-04 Update for Windows 11 Version 22H2 for x64-based Systems (KB4023057)            | Installed         | 20230512151545.785797-000 | 2024-01-24 01:28:08 |
| 29 | {f44ea661-292a-45af-aeda-94a33429e09c} | 2023-04 Update for Windows 11 Version 22H2 for x64-based Systems (KB4023057)            | Install Started   | 20230512151544.444812-000 | 2024-01-24 01:28:08 |
| 30 | {7d2c9b43-ed1e-453a-8f90-3cde5808d99d} | 2023-05 Cumulative Update for Windows 11 Version 22H2 for x64-based Systems (KB5026372) | Install Started   | 20230512124435.139438-000 | 2024-01-24 01:28:08 |

### em_12_kernel_versions table

|    |   MajorVersion |   MinorVersion |   BuildVersion |   QfeVersion |   ServiceVersion |   BootMode | StartTime                | added_on            |
|---:|---------------:|---------------:|---------------:|-------------:|-----------------:|-----------:|:-------------------------|:--------------------|
|  0 |             10 |              0 |          22621 |         2861 |                0 |          0 | 2023-12-22T13:02:32.500Z | 2024-01-24 01:45:54 |
|  1 |             10 |              0 |          22621 |         2861 |                0 |          0 | 2023-12-15T12:57:32.500Z | 2024-01-24 01:45:54 |
|  2 |             10 |              0 |          22621 |         2861 |                0 |          0 | 2023-12-15T06:04:24.500Z | 2024-01-24 01:45:54 |
|  3 |             10 |              0 |          22621 |         2715 |                0 |          0 | 2023-12-14T13:41:28.500Z | 2024-01-24 01:45:54 |
|  4 |             10 |              0 |          22621 |         2715 |                0 |          0 | 2023-11-17T22:47:25.500Z | 2024-01-24 01:45:54 |
|  5 |             10 |              0 |          22621 |         2715 |                0 |          0 | 2023-11-17T22:45:37.500Z | 2024-01-24 01:45:54 |
|  6 |             10 |              0 |          22621 |         2428 |                0 |          0 | 2023-11-16T13:05:40.500Z | 2024-01-24 01:45:54 |
|  7 |             10 |              0 |          22621 |         2428 |                0 |          0 | 2023-11-06T12:52:57.500Z | 2024-01-24 01:45:54 |
|  8 |             10 |              0 |          22621 |         2428 |                0 |          0 | 2023-10-17T15:15:01.500Z | 2024-01-24 01:45:54 |
|  9 |             10 |              0 |          22621 |         2428 |                0 |          0 | 2023-10-13T11:57:17.500Z | 2024-01-24 01:45:54 |
| 10 |             10 |              0 |          22621 |         2428 |                0 |          0 | 2023-10-13T03:49:08.500Z | 2024-01-24 01:45:54 |
| 11 |             10 |              0 |          22621 |         2283 |                0 |          0 | 2023-10-06T22:32:31.500Z | 2024-01-24 01:45:54 |
| 12 |             10 |              0 |          22621 |         2283 |                0 |          0 | 2023-10-03T01:28:52.500Z | 2024-01-24 01:45:54 |
| 13 |             10 |              0 |          22621 |         2283 |                0 |          0 | 2023-09-24T19:05:06.500Z | 2024-01-24 01:45:54 |
| 14 |             10 |              0 |          22621 |         2283 |                0 |          0 | 2023-09-15T12:01:10.500Z | 2024-01-24 01:45:54 |
| 15 |             10 |              0 |          22621 |         2134 |                0 |          0 | 2023-09-08T22:32:42.500Z | 2024-01-24 01:45:54 |
| 16 |             10 |              0 |          22621 |         2134 |                0 |          0 | 2023-09-06T22:25:44.500Z | 2024-01-24 01:45:54 |
| 17 |             10 |              0 |          22621 |         2134 |                0 |          0 | 2023-09-05T23:36:15.500Z | 2024-01-24 01:45:54 |
| 18 |             10 |              0 |          22621 |         2134 |                0 |          0 | 2023-08-27T19:43:13.500Z | 2024-01-24 01:45:54 |
| 19 |             10 |              0 |          22621 |         2134 |                0 |          0 | 2023-08-09T02:53:10.500Z | 2024-01-24 01:45:54 |
| 20 |             10 |              0 |          22621 |         1992 |                0 |          0 | 2023-08-09T02:51:23.500Z | 2024-01-24 01:45:54 |

### em_13_eicar_removed table

|    | File                          | Removed   | created_at          | added_on            |
|---:|:------------------------------|:----------|:--------------------|:--------------------|
|  0 | EICAR-2023-12-28_19-05-38.txt | Success   | 2023-12-29 01:05:38 | 2024-01-24 01:49:55 |
|  1 | EICAR-2024-01-06_21-31-07.txt | Success   | 2024-01-07 03:31:07 | 2024-01-24 01:49:55 |
|  2 | EICAR-2024-01-07_10-17-53.txt | Success   | 2024-01-07 16:17:53 | 2024-01-24 01:49:55 |
|  3 | EICAR-2024-01-07_16-21-13.txt | Success   | 2024-01-07 16:21:13 | 2024-01-24 01:49:55 |
|  4 | EICAR-2024-01-07_16-23-26.txt | Success   | 2024-01-07 16:23:26 | 2024-01-24 01:49:55 |
|  5 | EICAR-2024-01-09_01-31-02.txt | Success   | 2024-01-09 01:31:02 | 2024-01-24 01:49:55 |
|  6 | EICAR-2024-01-09_02-57-55.txt | Success   | 2024-01-09 02:57:55 | 2024-01-24 01:49:55 |
|  7 | EICAR-2024-01-09_13-02-12.txt | Success   | 2024-01-09 13:02:13 | 2024-01-24 01:49:55 |
|  8 | EICAR-2024-01-09_18-51-17.txt | Success   | 2024-01-09 18:51:17 | 2024-01-24 01:49:55 |
|  9 | EICAR-2024-01-09_22-55-08.txt | Success   | 2024-01-09 22:55:08 | 2024-01-24 01:49:55 |

### em_14_threat_scanning table

|    | created_at   |   count | added_on            |
|---:|:-------------|--------:|:--------------------|
|  0 | 2023-12-23   |      29 | 2024-01-24 02:01:58 |
|  1 | 2024-01-15   |       9 | 2024-01-24 02:01:58 |
|  2 | 2024-01-17   |       6 | 2024-01-24 02:01:58 |
|  3 | 2024-01-14   |       6 | 2024-01-24 02:01:58 |
|  4 | 2023-12-24   |       5 | 2024-01-24 02:01:58 |
|  5 | 2024-01-12   |       5 | 2024-01-24 02:01:58 |
|  6 | 2024-01-09   |       5 | 2024-01-24 02:01:58 |
|  7 | 2024-01-10   |       5 | 2024-01-24 02:01:58 |
|  8 | 2024-01-11   |       4 | 2024-01-24 02:01:58 |
|  9 | 2024-01-07   |       4 | 2024-01-24 02:01:58 |
| 10 | 2023-12-25   |       4 | 2024-01-24 02:01:58 |
| 11 | 2024-01-16   |       3 | 2024-01-24 02:01:58 |
| 12 | 2024-01-13   |       2 | 2024-01-24 02:01:58 |
| 13 | 2023-12-29   |       2 | 2024-01-24 02:01:58 |
| 14 | 2024-01-18   |       2 | 2024-01-24 02:01:58 |
| 15 | 2023-12-26   |       1 | 2024-01-24 02:01:58 |
| 16 | 2024-01-19   |       1 | 2024-01-24 02:01:58 |

### em_15_external_ports table

|    | mac                                                              | ip                                                               | port   | state   | reason   | name   | created_at          | added_on            |
|---:|:-----------------------------------------------------------------|:-----------------------------------------------------------------|:-------|:--------|:---------|:-------|:--------------------|:--------------------|
|  0 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-23 23:07:54 | 2024-01-25 00:04:57 |
|  1 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-23 23:13:33 | 2024-01-25 00:04:57 |
|  2 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-24 00:41:17 | 2024-01-25 00:04:57 |
|  3 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-24 01:46:09 | 2024-01-25 00:04:57 |
|  4 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-24 01:51:02 | 2024-01-25 00:04:57 |
|  5 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-24 04:08:14 | 2024-01-25 00:04:57 |
|  6 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-24 16:15:21 | 2024-01-25 00:04:57 |
|  7 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-25 04:11:26 | 2024-01-25 00:04:57 |
|  8 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-25 04:39:38 | 2024-01-25 00:04:57 |
|  9 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-25 04:47:43 | 2024-01-25 00:04:57 |
| 10 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2023-12-25 16:57:43 | 2024-01-25 00:04:57 |
| 11 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2024-01-07 03:37:08 | 2024-01-25 00:04:57 |
| 12 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2024-01-09 01:31:29 | 2024-01-25 00:04:57 |
| 13 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2024-01-09 02:58:20 | 2024-01-25 00:04:57 |
| 14 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2024-01-09 13:02:39 | 2024-01-25 00:04:57 |
| 15 | ee5b14ae53df0955c3b4d959122c833e10080f243d37885b47c92186a4a2ad55 | 2f21d087e5028db990723f46239084beb5649e0250108c64ff0d12e43714b512 |        |         |          |        | 2024-01-09 18:51:43 | 2024-01-25 00:04:57 |


### em_16_internal_ports table

|    | mac                                                              |   count | added_on            |
|---:|:-----------------------------------------------------------------|--------:|:--------------------|
|  0 | 130e9ed0ca95a3e2f4f4fb31850b81c4574300ba63c59b3d484f902a2ce36fc8 |       5 | 2024-01-25 00:21:29 |
|  1 | 3c400febdcdcbd90b46ad465cae771fe88b41cf5b9036d03e63c9026d61553db |       2 | 2024-01-25 00:21:29 |
|  2 | 4fbe27129b165da3e54850cea9a62cbf5c2ff960419446aaa43b022ffb3bc52c |       5 | 2024-01-25 00:21:29 |
|  3 | 76373ac195b1509ac4b61b2a44b6e5be3cc9bde9787f18cde90c88200ba45237 |       2 | 2024-01-25 00:21:29 |
|  4 | 7745cbc01814a790e4a4025de7afc49357b5db057c89cbae43704e9a02f4df2a |       3 | 2024-01-25 00:21:29 |
|  5 | 893abbc7a64320267e18673bc19c736c2675d8f6f4e7e06ea686ba1100e2cc59 |       5 | 2024-01-25 00:21:29 |
|  6 | 130e9ed0ca95a3e2f4f4fb31850b81c4574300ba63c59b3d484f902a2ce36fc8 |       5 | 2024-01-25 00:21:59 |
|  7 | 3c400febdcdcbd90b46ad465cae771fe88b41cf5b9036d03e63c9026d61553db |       2 | 2024-01-25 00:21:59 |
|  8 | 4fbe27129b165da3e54850cea9a62cbf5c2ff960419446aaa43b022ffb3bc52c |       5 | 2024-01-25 00:21:59 |
|  9 | 76373ac195b1509ac4b61b2a44b6e5be3cc9bde9787f18cde90c88200ba45237 |       2 | 2024-01-25 00:21:59 |
| 10 | 7745cbc01814a790e4a4025de7afc49357b5db057c89cbae43704e9a02f4df2a |       3 | 2024-01-25 00:21:59 |
| 11 | 893abbc7a64320267e18673bc19c736c2675d8f6f4e7e06ea686ba1100e2cc59 |       5 | 2024-01-25 00:21:59 |
| 12 | 130e9ed0ca95a3e2f4f4fb31850b81c4574300ba63c59b3d484f902a2ce36fc8 |       5 | 2024-01-25 01:31:47 |
| 13 | 3c400febdcdcbd90b46ad465cae771fe88b41cf5b9036d03e63c9026d61553db |       2 | 2024-01-25 01:31:47 |
| 14 | 4fbe27129b165da3e54850cea9a62cbf5c2ff960419446aaa43b022ffb3bc52c |       5 | 2024-01-25 01:31:47 |
| 15 | 76373ac195b1509ac4b61b2a44b6e5be3cc9bde9787f18cde90c88200ba45237 |       2 | 2024-01-25 01:31:47 |
| 16 | 7745cbc01814a790e4a4025de7afc49357b5db057c89cbae43704e9a02f4df2a |       3 | 2024-01-25 01:31:47 |
| 17 | 893abbc7a64320267e18673bc19c736c2675d8f6f4e7e06ea686ba1100e2cc59 |       5 | 2024-01-25 01:31:47 |

### em_18_rdp_enabled table

|    | Name                                                             | RDPUsers      | RDPEnabled   | NLAEnabled   | created_at          | added_on            |
|---:|:-----------------------------------------------------------------|:--------------|:-------------|:-------------|:--------------------|:--------------------|
|  0 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-27 15:57:20 | 2024-01-25 00:30:38 |
|  1 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-27 15:57:20 | 2024-01-25 00:30:38 |
|  2 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-27 15:59:08 | 2024-01-25 00:30:38 |
|  3 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-27 15:59:08 | 2024-01-25 00:30:38 |
|  4 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-27 15:59:29 | 2024-01-25 00:30:38 |
|  5 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-27 15:59:29 | 2024-01-25 00:30:38 |
|  6 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-27 16:01:00 | 2024-01-25 00:30:38 |
|  7 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-27 16:01:00 | 2024-01-25 00:30:38 |
|  8 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-28 03:45:20 | 2024-01-25 00:30:38 |
|  9 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-28 03:45:20 | 2024-01-25 00:30:38 |
| 10 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-28 03:55:21 | 2024-01-25 00:30:38 |
| 11 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-28 03:55:21 | 2024-01-25 00:30:38 |
| 12 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-28 14:05:20 | 2024-01-25 00:30:38 |
| 13 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-28 14:05:20 | 2024-01-25 00:30:38 |
| 14 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-28 14:15:21 | 2024-01-25 00:30:38 |
| 15 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-28 14:15:21 | 2024-01-25 00:30:38 |
| 16 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-28 14:25:22 | 2024-01-25 00:30:38 |
| 17 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-28 14:25:22 | 2024-01-25 00:30:38 |
| 18 | 543e82e4861654adc411608a1d7773eeb3fda00ebad6410fdec9a4467534abc0 | Administrator | False        | True         | 2023-12-28 14:35:21 | 2024-01-25 00:30:38 |
| 19 | ceb1036843f98d3ec4b161b3b3eb0f11585206f29a30bd8e552c1157a9c5b709 | Administrator | False        | True         | 2023-12-28 14:35:21 | 2024-01-25 00:30:38 |

### em_19_usb_devices table

|    | Id                                                               | created_at          | added_on            |
|---:|:-----------------------------------------------------------------|:--------------------|:--------------------|
|  0 | 6f738a78d831d3ed51e1bcf324dd99a00aeae8decff747104a85a8494d10afef | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  1 | d3f26510ae67d8ea1ffcbe2f25d33ef1c521bd9e73caec19edeab0f538f8a595 | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  2 | 192e6665320fe74a1235903f923f9af5cf9dbe2eed4ead77c93681f804924ae1 | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  3 | e3ecf7f62367225b0eae99aadc7cf1b8cdf8fdbd90b1fd429d19f4bd97aa6fb5 | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  4 | 86a9d7ef19b32f05ba713f619a86d9e067e35974cd77598f20e353fa6d43fec5 | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  5 | cfb2dd00c9237293a76259fb29d2f201614d54d36fd002e9b2cb29dca25e4bec | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  6 | 0708500bfede35b57a2875734dfabc2b947122e6c2743f8111821f1007115004 | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  7 | 6a977c1de24bab2717c21660d0e186dec906be07f0fa3e7385027923a3ba6379 | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  8 | e33eb23ca8e8fb95a8a173fe602e022f6f57b2e4eabdd7d65a5bcc379507041b | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
|  9 | 6224b8f504ca251a54869e388fa51020a01e8bae4d6d20bf61919587684c7f4e | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
| 10 | dfed5ed95b6fa7ac1d89946cec9b0d4ecc315b652a18b3e1563a53f46410061e | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
| 11 | 63701db8aaab17dd29b2ca1a90b053f7f5cf38f5a23694d4e0129edc4a59e90f | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
| 12 | 22b5294b465012b83bc6e171e154f51a56ae4a449ad3b750fa4e4355a073d19a | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
| 13 | 33f6706b7754adbb165c0d328f36dbe096eaeae42c6f4368a0a31f85c5461a9f | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
| 14 | 53cdc7e3e8a90c05dae8ecb1fe9186a7ff1fd63267b7ca9bbcf486a7507a3513 | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
| 15 | 71f4a4e753c2c650356cdacdf0c70ce5fcf19701f03e5a009b7f04817e3c0dc4 | 2023-12-29 17:48:25 | 2024-01-25 00:47:12 |
| 16 | cfb2dd00c9237293a76259fb29d2f201614d54d36fd002e9b2cb29dca25e4bec | 2024-01-15 14:01:31 | 2024-01-25 00:47:12 |
| 17 | 41623171c397e1abff2fb43b2a176e4e05ecade3572761e777bcc91f8ac680fe | 2024-01-15 14:01:31 | 2024-01-25 00:47:12 |
| 18 | 89eb115f33bff79636c93e4617d33bf7bb0baf664b5d7b0ec20c434931e0a473 | 2024-01-15 14:01:31 | 2024-01-25 00:47:12 |
| 19 | dfed5ed95b6fa7ac1d89946cec9b0d4ecc315b652a18b3e1563a53f46410061e | 2024-01-15 14:01:31 | 2024-01-25 00:47:12 |
| 20 | 63701db8aaab17dd29b2ca1a90b053f7f5cf38f5a23694d4e0129edc4a59e90f | 2024-01-19 00:07:51 | 2024-01-25 00:47:12 |
| 21 | 43fb93416d0a11b58dd3fe93e55008e8dc642ff1c5221add9bab76d2de07b261 | 2024-01-21 19:51:27 | 2024-01-25 00:47:12 |
| 22 | c4a23eff0c230742f49453c6e6c9b7ef0ec52a5ee16d89dfbafdb66ca0cdac76 | 2024-01-21 19:51:27 | 2024-01-25 00:47:12 |

## em_19_usb_policy table
|    | Path                                                                               | Name                     | Data                                     | created_at          | added_on            |
|---:|:-----------------------------------------------------------------------------------|:-------------------------|:-----------------------------------------|:--------------------|:--------------------|
|  0 | HKLM:\Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions               | DenyUnspecified          | 1                                        | 2024-01-29 01:14:12 | 2024-01-29 01:27:30 |
|  1 | HKLM:\Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions               | DenyDeviceIDs            | 1                                        | 2024-01-29 01:14:12 | 2024-01-29 01:27:30 |
|  2 | HKLM:\Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions               | DenyDeviceIDsRetroactive | 0                                        | 2024-01-29 01:14:12 | 2024-01-29 01:27:30 |
|  3 | HKLM:\Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions\DenyDeviceIDs | 1                        | USBSTOR\Disk_USB_____SanDisk_3.2Gen11.00 | 2024-01-29 01:14:12 | 2024-01-29 01:27:30 |

### em_20_users table

|    | sid                                                              |   priv |   last_logon |   password_days | account_disabled   | created_at          | added_on            |
|---:|:-----------------------------------------------------------------|-------:|-------------:|----------------:|:-------------------|:--------------------|:--------------------|
|  0 | 1511ffaa098ae9d73d28580afdb1da4807074959250cea478abef01ab05d716c |      0 |            0 |               0 | True               | 2024-01-15 22:35:06 | 2024-01-25 00:57:55 |
|  1 | e69847cdc5bdb2c86cb30d7bddf5e8a034e1a9f42bd64b920195f9b21204df9a |      2 |            0 |               0 | True               | 2024-01-15 22:35:06 | 2024-01-25 00:57:55 |
|  2 | cd350f071cb77cbe9df50c2dca42037bbf15fc5b7aa091ba5532a10a7a4bc9cd |      0 |            0 |               0 | True               | 2024-01-15 22:35:06 | 2024-01-25 00:57:55 |
|  3 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 |      2 |   1699412482 |            1218 | False              | 2024-01-20 21:35:25 | 2024-01-25 00:57:55 |
|  4 | 2cb03e2b97696acfd2ba9253871b82de8eeaf1858eeed4aa45cc9e811a350e17 |      1 |   1705359224 |               5 | False              | 2024-01-20 23:22:48 | 2024-01-25 00:57:55 |

### em_20_admin_logins table

|    | Sid                                                              | LogonType   |   EventIdentifier | LogonID    | ElevatedToken   | TimeGenerated             | added_on            |
|---:|:-----------------------------------------------------------------|:------------|------------------:|:-----------|:----------------|:--------------------------|:--------------------|
|  0 | c259d92dc0180a37e52f9842113f74ddde0b5ee9a58c5b7a2ec43e671d2da63d | 5           |              4624 | 0x29ffd969 | Yes             | 20240115223725.310710-000 | 2024-01-25 01:28:24 |
|  1 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 2           |              4634 | 0x299f7a8d |                 | 20240115220736.637112-000 | 2024-01-25 01:28:24 |
|  2 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4634 | 0x299f8d11 |                 | 20240115220736.637023-000 | 2024-01-25 01:28:24 |
|  3 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 2           |              4634 | 0x299f7ad2 |                 | 20240115220736.636860-000 | 2024-01-25 01:28:24 |
|  4 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4634 | 0x299f8f90 |                 | 20240115220736.636820-000 | 2024-01-25 01:28:24 |
|  5 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4624 | 0x299f8f90 | No              | 20240115220736.636564-000 | 2024-01-25 01:28:24 |
|  6 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4624 | 0x299f8d11 | Yes             | 20240115220736.636550-000 | 2024-01-25 01:28:24 |
|  7 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 11          |              4624 | 0x299f7ad2 | No              | 20240115220736.597250-000 | 2024-01-25 01:28:24 |
|  8 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 11          |              4624 | 0x299f7a8d | Yes             | 20240115220736.597240-000 | 2024-01-25 01:28:24 |
|  9 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4634 | 0x28de7112 |                 | 20240115174559.828962-000 | 2024-01-25 01:28:24 |
| 10 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4634 | 0x28de717a |                 | 20240115174559.828837-000 | 2024-01-25 01:28:24 |
| 11 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4624 | 0x28de717a | No              | 20240115174559.828738-000 | 2024-01-25 01:28:24 |
| 12 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4624 | 0x28de7112 | Yes             | 20240115174559.828726-000 | 2024-01-25 01:28:24 |
| 13 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 11          |              4624 | 0x28de6c64 | No              | 20240115174559.802897-000 | 2024-01-25 01:28:24 |
| 14 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 11          |              4624 | 0x28de6c1f | Yes             | 20240115174559.802886-000 | 2024-01-25 01:28:24 |
| 15 | 66ad7abf2900af71b4a4b6f07ba6bd791895feb1d4ad6ba475d3a0b3062f31cb | 2           |              4634 | 0x161a9    |                 | 20240115174555.497005-000 | 2024-01-25 01:28:24 |
| 16 | 66ad7abf2900af71b4a4b6f07ba6bd791895feb1d4ad6ba475d3a0b3062f31cb | 2           |              4634 | 0x161e0    |                 | 20240115174555.496954-000 | 2024-01-25 01:28:24 |
| 17 | 3c2f336bee00bd973b72da9babcb402f50281edd4fa724aea31a7c6e90ce6f87 | 2           |              4634 | 0x15251    |                 | 20240115174554.269278-000 | 2024-01-25 01:28:24 |
| 18 | 3dca084076ca11c67815953cee7827dcdfe6ddca62d6e8340d8629871ad7308f | 2           |              4624 | 0x28dc5f92 | No              | 20240115174554.077908-000 | 2024-01-25 01:28:24 |
| 19 | 3dca084076ca11c67815953cee7827dcdfe6ddca62d6e8340d8629871ad7308f | 2           |              4624 | 0x28dc5f67 | Yes             | 20240115174554.077897-000 | 2024-01-25 01:28:24 |
| 20 | fe0f50e4f339ae7bc69025d16463adeff8e37179ce63554b42716427a40cbbb6 | 2           |              4624 | 0x28dc514a | No              | 20240115174554.047752-000 | 2024-01-25 01:28:24 |
| 21 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | Logoff      |              4647 | 0x16f425   |                 | 20240115174552.928335-000 | 2024-01-25 01:28:24 |
| 22 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 2           |              4634 | 0x273c8cbf |                 | 20240115163705.058231-000 | 2024-01-25 01:28:24 |
| 23 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4634 | 0x273c9a4d |                 | 20240115163705.058225-000 | 2024-01-25 01:28:24 |
| 24 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 2           |              4634 | 0x273c8d05 |                 | 20240115163705.057961-000 | 2024-01-25 01:28:24 |
| 25 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4634 | 0x273c9c21 |                 | 20240115163705.057920-000 | 2024-01-25 01:28:24 |
| 26 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4624 | 0x273c9c21 | No              | 20240115163705.057750-000 | 2024-01-25 01:28:24 |
| 27 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 7           |              4624 | 0x273c9a4d | Yes             | 20240115163705.057726-000 | 2024-01-25 01:28:24 |
| 28 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 11          |              4624 | 0x273c8d05 | No              | 20240115163705.023857-000 | 2024-01-25 01:28:24 |
| 29 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 11          |              4624 | 0x273c8cbf | Yes             | 20240115163705.023846-000 | 2024-01-25 01:28:24 |
| 30 | 26e91687ff81e9a4eba02b7e00abbbe444eb2f715f8623c27324d51a2bb9ce04 | 2           |              4634 | 0x2a340353 |                 | 20240115224909.062847-000 | 2024-01-25 01:28:24 |