# vector-db-benchmark

![Screenshot from 2022-08-23 14-10-01](https://user-images.githubusercontent.com/1935623/186516524-a61098d4-bca6-4aeb-acbe-d969cf30674e.png)

> [View results](https://qdrant.tech/benchmarks/)

There are various vector search engines available, and each of them may offer
a different set of features and efficiency. But how do we measure the
performance? There is no clear definition and in a specific case you
may worry about a specific thing, while not paying much attention to other aspects. This
project is a general framework for benchmarking different engines under the
same hardware constraints, so you can choose what works best for you.

Running any benchmark requires choosing an engine, a dataset and defining the
scenario against which it should be tested. A specific scenario may assume
running the server in a single or distributed mode, a different client
implementation and the number of client instances.

## How to run a benchmark?

Benchmarks are implemented in server-client mode, meaning that the server is
running in a single machine, and the client is running on another.

### Run the server

All engines are served using docker compose. The configuration is in the [servers](./engine/servers/).

To launch the server instance, run the following command:

```bash
cd ./engine/servers/<engine-configuration-name>
docker compose up
```

Containers are expected to expose all necessary ports, so the client can connect to them.

### Run the client

Install dependencies:

```bash
pip install poetry
poetry install
```

Run the benchmark:

```bash
Usage: run.py [OPTIONS]

  Example: python3 -m run --engines *-m-16-* --datasets glove-*

Options:
  --engines TEXT                  [default: *]
  --datasets TEXT                 [default: *]
  --host TEXT                     [default: localhost]
  --skip-upload / --no-skip-upload
                                  [default: no-skip-upload]
  --install-completion            Install completion for the current shell.
  --show-completion               Show completion for the current shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
```

Command allows you to specify wildcards for engines and datasets.
Results of the benchmarks are stored in the `./results/` directory.

## How to update benchmark parameters?

Each engine has a configuration file, which is used to define the parameters for the benchmark.
Configuration files are located in the [configuration](./experiments/configurations/) directory.

Each step in the benchmark process is using a dedicated configuration's path:

* `connection_params` - passed to the client during the connection phase.
* `collection_params` - parameters, used to create the collection, indexing parameters are usually defined here.
* `upload_params` - parameters, used to upload the data to the server.
* `search_params` - passed to the client during the search phase. Framework allows multiple search configurations for the same experiment run.

Exact values of the parameters are individual for each engine.

## How to register a dataset?

Datasets are configured in the [datasets/datasets.json](./datasets/datasets.json) file.
Framework will automatically download the dataset and store it in the [datasets](./datasets/) directory.

## How to implement a new engine?

There are a few base classes that you can use to implement a new engine.

* `BaseConfigurator` - defines methods to create collections, setup indexing parameters.
* `BaseUploader` - defines methods to upload the data to the server.
* `BaseSearcher` - defines methods to search the data.

See the examples in the [clients](./engine/clients) directory.

Once all the necessary classes are implemented, you can register the engine in the [ClientFactory](./engine/clients/client_factory.py).

## Reproduce our published benchmark suite

In this section are step by step instructions to reproduce the benchmark suite that we have published internal and externally.

If you are interested just in version and machine information, go to the last section. 

### Qdrant

For Qdrant benchmarking, you need to start a docker-based Qdrant server and then run a benchmark script.

#### Qdrant server (single-node)

```
# Run the qdrant server in a 'screen' or 'tmux'
cd engine/servers/qdrant-single-node
docker compose up
```

##### Qdrant benchmarks, deep-image-96-angular

```
# Make sure the right qdrant single-node server has started (see above).
./run_qdrant_benchmarks.sh
```

### Weaviate

For Weaviate benchmarking, you need to start a docker-based Qdrant server and then run a benchmark script.

#### Weaviate server (single-node)

```
# Run the weaviate server in a 'screen' or 'tmux'
cd engine/servers/weaviate-single-node
docker compose up
```

#### Weaviate benchmarks, deep-image-96-angular

```
# Make sure the right weaviate single-node server has started (see above).
./run_weaviate_benchmarks.sh
```

### GSI FVS

For GSI FVS benchmarking, you need to start a docker-based FVS server and then run a few benchmark scripts.


### GSI FVS Server

```
# We ran the FVS version=0.9.5.4 using a slightly modified script from IL/Nadav located at fvs_server/0.4.1-alpha15/backend/run_local_george_and_jacob.sh.
# We ran our benchmarks on a machine with 4 LEDA GSI boards, Host CPU="Intel(R) Xeon(R) Gold 6230R CPU @ 2.10GHz", DRAM=800GB.
# In general, you need to make sure the containers "training_manager" and "float32" start up properly.  We noticed the startup of those containers could take a few seconds.
# We also ran the sanity check program called "fvs_test.py" in this directory after starting the server.  Note that you may need to change file paths at the top of the file.
# If you run into issue, I recommend stopping and removing all the docker containers via "docker stop $(docker ps -a -q)" and then "docker rm $(docker ps -a -q)" and
# also removing all the cached cluster data directories that live in /home/public/elastic_similarity/python-training_manager/cache, rebooting, and then launch the script
# and then removing a rows from the "trains" tables in the postgres docker container (esp. "clusters_trains")."

screen
cd ./0.4.1-alpha15/backend
./run_local_george_and_jacob.sh
# Note that this will log all the docker containers at the same time 
# and it could take several seconds for the top-level containers to start
# (i.e., training-manager and float32 containers).
```

Make sure to activate your python environment before running these benchmarks.

#### GSI FVS benchmarks

```
# Each of the following scripts runs several different GSI configurations.
# Between each script below we reset the GSI FVS docker containers via stop/rm and cleared the training cache, removed rows from "trains" postgres tables, and reboot the system.
./run_gsi-128_benchmarks.sh
./run_gsi-256_benchmarks.sh
./run_gsi-512_benchmarks.sh
./run_gsi-768_benchmarks.sh
./run_gsi-misc_benchmarks.sh
```

### HNSWLib

Note that there is no server associated with the HNSWLib benchmarks.  The relevant Qdrant engine scripts import the hnswlib package.

#### HNSWLib benchmarks

```
# We reboot the system before running the script.
./run_hnswlib_benchmarks.sh 
```

### GXL 

Note that there is no server associated with the GXL benchmarks. The relevant Qdrant engine scripts invoke the GXL scripts and use the hnswlib package.

#### GXL benchmarks


### Appendix: Software version and machine info

#### Software 

*  Python 3.10.13 (main, Sep 11 2023, 13:44:35) [GCC 11.2.0] on linux
*  conda 23.7.4
*  Ubuntu 20.04.6 LTS
*  Linux sv7-apu11 5.4.0-136-generic #153-Ubuntu SMP Thu Nov 24 15:56:58 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
*  hnswlib: 0.8.0 
*  weaviate: semitechnologies/weaviate:1.19.9 (see weaviate single node docker yaml for additional server config details)
*  qdrant: qdrant/qdrant:v1.1.0 (see qdrant single node docker yaml for additional server config details)
*  GXL: run-gxl=v1.2, run-gxl-cen-gen=1.2, run-make-symmetric=1.2, gxl-hnsw=169856 bytes,  gxl-hnsw-idx-gen=104096 bytes
*  FVS: 0.9.5.4 (see FVS server docker yaml for additional server config details)


#### Machine Info

#### cpu info via "lscpu"

```
Architecture:                    x86_64
CPU op-mode(s):                  32-bit, 64-bit
Byte Order:                      Little Endian
Address sizes:                   46 bits physical, 48 bits virtual
CPU(s):                          104
On-line CPU(s) list:             0-103
Thread(s) per core:              2
Core(s) per socket:              26
Socket(s):                       2
NUMA node(s):                    2
Vendor ID:                       GenuineIntel
CPU family:                      6
Model:                           85
Model name:                      Intel(R) Xeon(R) Gold 6230R CPU @ 2.10GHz
Stepping:                        7
CPU MHz:                         1000.577
CPU max MHz:                     4000.0000
CPU min MHz:                     1000.0000
BogoMIPS:                        4200.00
Virtualization:                  VT-x
L1d cache:                       1.6 MiB
L1i cache:                       1.6 MiB
L2 cache:                        52 MiB
L3 cache:                        71.5 MiB
NUMA node0 CPU(s):               0-25,52-77
NUMA node1 CPU(s):               26-51,78-103
Vulnerability Itlb multihit:     KVM: Mitigation: Split huge pages
Vulnerability L1tf:              Not affected
Vulnerability Mds:               Not affected
Vulnerability Meltdown:          Not affected
Vulnerability Mmio stale data:   Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable
Vulnerability Retbleed:          Mitigation; Enhanced IBRS
Vulnerability Spec store bypass: Mitigation; Speculative Store Bypass disabled via prctl and seccomp
Vulnerability Spectre v1:        Mitigation; usercopy/swapgs barriers and __user pointer sanitization
Vulnerability Spectre v2:        Mitigation; Enhanced IBRS, IBPB conditional, RSB filling, PBRSB-eIBRS SW sequence
Vulnerability Srbds:             Not affected
Vulnerability Tsx async abort:   Mitigation; TSX disabled
Flags:                           fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc a
                                 rt arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pci
                                 d dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb cat_l3 cdp_l3 invpcid_single intel_p
                                 pin ssbd mba ibrs ibpb stibp ibrs_enhanced tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm mpx rdt_a avx512f 
                                 avx512dq rdseed adx smap clflushopt clwb intel_pt avx512cd avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local dther
                                 m ida arat pln pts pku ospke avx512_vnni md_clear flush_l1d arch_capabilities
```

##### memory info via "free"

```
$ free
              total
Mem:      791210564
Swap:       8388604
```

##### SSD info via ""
```
$ sudo hdparm -I /dev/sda2
[sudo] password for gwilliams: 

/dev/sda2:

ATA device, with non-removable media
	Model Number:       Micron_5300_MTFDDAK1T9TDS               
	Serial Number:      214031A57D1D
	Firmware Revision:  D3MU001
	Transport:          Serial, ATA8-AST, SATA 1.0a, SATA II Extensions, SATA Rev 2.5, SATA Rev 2.6, SATA Rev 3.0
Standards:
	Used: unknown (minor revision code 0xffff) 
	Supported: 11 10 9 8 7 6 5 
	Likely used: 11
Configuration:
	Logical		max	current
	cylinders	16383	0
	heads		16	0
	sectors/track	63	0
	--
	LBA    user addressable sectors:   268435455
	LBA48  user addressable sectors:  3750748848
	Logical  Sector size:                   512 bytes
	Physical Sector size:                  4096 bytes
	Logical Sector-0 offset:                  0 bytes
	device size with M = 1024*1024:     1831420 MBytes
	device size with M = 1000*1000:     1920383 MBytes (1920 GB)
	cache/buffer size  = unknown
	Form Factor: 2.5 inch
	Nominal Media Rotation Rate: Solid State Device
Capabilities:
	LBA, IORDY(can be disabled)
	Queue depth: 32
	Standby timer values: spec'd by Standard, with device specific minimum
	R/W multiple sector transfer: Max = 16	Current = 16
	Advanced power management level: 254
	DMA: mdma0 mdma1 mdma2 udma0 udma1 udma2 udma3 udma4 udma5 *udma6 
	     Cycle time: min=120ns recommended=120ns
	PIO: pio0 pio1 pio2 pio3 pio4 
	     Cycle time: no flow control=120ns  IORDY flow control=120ns
Commands/features:
	Enabled	Supported:
	   *	SMART feature set
	    	Security Mode feature set
	   *	Power Management feature set
	   *	Write cache
	   *	Look-ahead
	   *	WRITE_BUFFER command
	   *	READ_BUFFER command
	   *	NOP cmd
	   *	DOWNLOAD_MICROCODE
	   *	Advanced Power Management feature set
	   *	48-bit Address feature set
	   *	Mandatory FLUSH_CACHE
	   *	FLUSH_CACHE_EXT
	   *	SMART error logging
	   *	SMART self-test
	   *	General Purpose Logging feature set
	   *	WRITE_{DMA|MULTIPLE}_FUA_EXT
	   *	64-bit World wide name
	   *	IDLE_IMMEDIATE with UNLOAD
	    	Write-Read-Verify feature set
	   *	WRITE_UNCORRECTABLE_EXT command
	   *	{READ,WRITE}_DMA_EXT_GPL commands
	   *	Segmented DOWNLOAD_MICROCODE
	    	unknown 119[8]
	   *	Gen1 signaling speed (1.5Gb/s)
	   *	Gen2 signaling speed (3.0Gb/s)
	   *	Gen3 signaling speed (6.0Gb/s)
	   *	Native Command Queueing (NCQ)
	   *	Phy event counters
	   *	NCQ priority information
	   *	READ_LOG_DMA_EXT equivalent to READ_LOG_EXT
	   *	DMA Setup Auto-Activate optimization
	   *	Software settings preservation
	    	unknown 78[12]
	   *	SMART Command Transport (SCT) feature set
	   *	SCT Write Same (AC2)
	   *	SCT Features Control (AC4)
	   *	SCT Data Tables (AC5)
	   *	SANITIZE_ANTIFREEZE_LOCK_EXT command
	   *	SANITIZE feature set
	   *	CRYPTO_SCRAMBLE_EXT command
	   *	OVERWRITE_EXT command
	   *	BLOCK_ERASE_EXT command
	   *	DOWNLOAD MICROCODE DMA command
	   *	WRITE BUFFER DMA command
	   *	READ BUFFER DMA command
	   *	Data Set Management TRIM supported (limit 8 blocks)
	   *	Deterministic read ZEROs after TRIM
Security: 
	Master password revision code = 65534
		supported
	not	enabled
	not	locked
		frozen
	not	expired: security count
		supported: enhanced erase
	2min for SECURITY ERASE UNIT. 2min for ENHANCED SECURITY ERASE UNIT.
Logical Unit WWN Device Identifier: 500a075131a57d1d
	NAA		: 5
	IEEE OUI	: 00a075
	Unique ID	: 131a57d1d
Checksum: correct
```

##### LEDA info via "ledagssh -o localhost"

```
$ ledag-ssh -o localhost
GSI Leda-G SSH
Starting................
Version: 100.12.0.5.1000.1
Not Connected
init ok
slot0 {'Apuc_Mask': '0xf', 'Dev_Name': 'dev-8600', 'FW Status': 'background', 'File_Name': '/dev/apu/mngt/m00', 'Log_State': 'File', 'Mac': '00:4e', 'Mem_Size': '15027142656', 'Version': '220.13.500.1'}
slot1 {'Apuc_Mask': '0xf', 'Dev_Name': 'dev-8700', 'FW Status': 'background', 'File_Name': '/dev/apu/mngt/m01', 'Log_State': 'File', 'Mac': '00:50', 'Mem_Size': '15027142656', 'Version': '220.13.500.1'}
slot2 {'Apuc_Mask': '0xf', 'Dev_Name': 'dev-af00', 'FW Status': 'background', 'File_Name': '/dev/apu/mngt/m02', 'Log_State': 'File', 'Mac': '60:92', 'Mem_Size': '15027142656', 'Version': '220.13.500.1'}
slot3 {'Apuc_Mask': '0xf', 'Dev_Name': 'dev-b000', 'FW Status': 'background', 'File_Name': '/dev/apu/mngt/m03', 'Log_State': 'File', 'Mac': '60:94', 'Mem_Size': '15027142656', 'Version': '220.13.500.1'}
Connected
```

### Appendix: Clearing training manager database

Locate the postgresql docker id and run the following below:

```
$ docker exec -it 6e8170c04f67 /bin/bash
bash-5.0# psql --port=14032 --dbname=caching_db --username=fvs_post_user -W
Password: 
psql (13.0)
Type "help" for help.

caching_db=# \dt
                List of relations
 Schema |      Name       | Type  |     Owner     
--------+-----------------+-------+---------------
 public | clusters_trains | table | fvs_post_user
 public | flat_trains     | table | fvs_post_user
 public | hnsw_trains     | table | fvs_post_user
(3 rows)

caching_db=# delete from clusters_trains
caching_db-# ;
DELETE 0
caching_db=# delete from flat_trains
caching_db-# ;
DELETE 1
caching_db=# delete from hnsw_trains;
DELETE 0
caching_db=# 
```
