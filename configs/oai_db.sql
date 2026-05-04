CREATE DATABASE IF NOT EXISTS oai_db;
USE oai_db;

CREATE TABLE IF NOT EXISTS AuthenticationSubscription (
  ueid varchar(15) NOT NULL,
  authenticationMethod varchar(25) NOT NULL,
  encPermanentKey varchar(50) NOT NULL,
  protectionParameterId varchar(50) DEFAULT NULL,
  sequenceNumber json DEFAULT NULL,
  authenticationManagementField varchar(20) DEFAULT NULL,
  algorithmId varchar(20) DEFAULT NULL,
  encOpcKey varchar(50) DEFAULT NULL,
  encTopcKey varchar(50) DEFAULT NULL,
  vectorGenerationInHss tinyint(1) DEFAULT NULL,
  n5gcAuthMethod varchar(15) DEFAULT NULL,
  rgAuthenticationInd tinyint(1) DEFAULT NULL,
  supi varchar(20) DEFAULT NULL,
  PRIMARY KEY (ueid)
);

CREATE TABLE IF NOT EXISTS AccessAndMobilitySubscriptionData (
  ueid varchar(15) NOT NULL,
  servingPlmnid varchar(15) NOT NULL,
  supportedFeatures varchar(50) DEFAULT NULL,
  gpsis json DEFAULT NULL,
  internalGroupIds json DEFAULT NULL,
  subscribedUeAmbr json DEFAULT NULL,
  nssai json DEFAULT NULL,
  ratRestrictions json DEFAULT NULL,
  forbiddenAreas json DEFAULT NULL,
  serviceAreaRestriction json DEFAULT NULL,
  coreNetworkTypeRestrictions json DEFAULT NULL,
  rfspIndex int DEFAULT NULL,
  subsRegTimer int DEFAULT NULL,
  ueUsageType int DEFAULT NULL,
  mpsPriority tinyint(1) DEFAULT NULL,
  mcsPriority tinyint(1) DEFAULT NULL,
  activeTime int DEFAULT NULL,
  sorInfo json DEFAULT NULL,
  sorInfoExpectInd tinyint(1) DEFAULT NULL,
  sorafRetrieval tinyint(1) DEFAULT NULL,
  sorUpdateIndicatorList json DEFAULT NULL,
  upuInfo json DEFAULT NULL,
  micoAllowed tinyint(1) DEFAULT NULL,
  sharedAmDataIds json DEFAULT NULL,
  subscribedDnnList json DEFAULT NULL,
  PRIMARY KEY (ueid, servingPlmnid)
);

CREATE TABLE IF NOT EXISTS SessionManagementSubscriptionData (
  ueid varchar(15) NOT NULL,
  servingPlmnid varchar(15) NOT NULL,
  singleNssai json NOT NULL,
  dnnConfigurations json DEFAULT NULL,
  internalGroupIds json DEFAULT NULL,
  sharedVnGroupDataIds json DEFAULT NULL,
  sharedDnnConfigurationsId varchar(50) DEFAULT NULL,
  odbPacketServices varchar(50) DEFAULT NULL,
  traceData json DEFAULT NULL,
  sharedTraceDataId varchar(50) DEFAULT NULL,
  expectedUeBehavioursList json DEFAULT NULL,
  suggestedPacketNumDlList json DEFAULT NULL,
  PRIMARY KEY (ueid, servingPlmnid)
);

INSERT INTO AuthenticationSubscription
(ueid, authenticationMethod, encPermanentKey, sequenceNumber, authenticationManagementField, algorithmId, encOpcKey, n5gcAuthMethod, supi)
VALUES
('208990000000001', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f',
 '{"sqn": "000000000020", "sqnScheme": "NON_TIME_BASED", "lastIndexes": {"ausf": 0}}',
 '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', '5G_AKA', '208990000000001')
ON DUPLICATE KEY UPDATE
encPermanentKey=VALUES(encPermanentKey),
encOpcKey=VALUES(encOpcKey);

INSERT INTO AccessAndMobilitySubscriptionData
(ueid, servingPlmnid, subscribedUeAmbr, nssai, subscribedDnnList)
VALUES
('208990000000001', '20895',
 '{"uplink":"1 Gbps","downlink":"1 Gbps"}',
 '{"defaultSingleNssais":[{"sst":1,"sd":"000001"}],"singleNssais":[{"sst":1,"sd":"000001"}]}',
 '["oai"]')
ON DUPLICATE KEY UPDATE
nssai=VALUES(nssai),
subscribedDnnList=VALUES(subscribedDnnList);

INSERT INTO SessionManagementSubscriptionData
(ueid, servingPlmnid, singleNssai, dnnConfigurations)
VALUES
('208990000000001', '20895',
 '{"sst":1,"sd":"000001"}',
 '{"oai":{"pduSessionTypes":{"defaultSessionType":"IPV4","allowedSessionTypes":["IPV4"]},"sscModes":{"defaultSscMode":"SSC_MODE_1","allowedSscModes":["SSC_MODE_1"]},"5gQosProfile":{"5qi":9,"arp":{"priorityLevel":15,"preemptCap":"NOT_PREEMPT","preemptVuln":"PREEMPTABLE"},"priorityLevel":15},"sessionAmbr":{"uplink":"1 Gbps","downlink":"1 Gbps"},"staticIpAddress":[{"ipv4Addr":"12.1.1.10"}]}}')
ON DUPLICATE KEY UPDATE
singleNssai=VALUES(singleNssai),
dnnConfigurations=VALUES(dnnConfigurations);
