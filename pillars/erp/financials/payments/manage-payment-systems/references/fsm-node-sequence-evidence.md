# MPS export-local NodeSequence evidence



## Producer
Read-only fphdev inspection of ConfigurationPackageAMHelper.createBusinessObjectCSVMetadataRowsForService: XML files/node paths are queried for pXmlRequestId, sorted by XML_NODE_PATH_ID, assigned incremental integers, and looked up for each service business object. The number is scoped to the produced export, not a permanent business-object identifier. addTranslationBOCSVMetadataRowForParent forwards the parent sequence and its XML file to the generated translation object.

## Consumer
XmlCSVAMImpl.prepareForTransform groups business objects by authoritative XML file, then paired XML path hierarchy level, then a TreeMap keyed by NodeSequence. Hierarchy traversal precedes sequence traversal. Require positive integers and reject collisions within the same XML file and hierarchy level. Do not impose cross-level numeric parent-before-child ordering. Preserve original metadata bytes unchanged when building a candidate.

## MPS file mapping
The captured SetupBusinessObjectSD.xml MPS rows explicitly map the seven service-owned business objects to IBY_PAYMENT_SYSTEM.xml. Each captured XmlNodePath matches the descriptor. The generated account-name translation object inherits that file from its definition parent through the source producer branch. ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL is a different TransmissionService object/file and is excluded from this eight-entity MPS contract.

## Qualification boundary
A real current cptcpuwqy export for J04 maps the root to sequence8, while earlier successful exports map it to1. Header/path/type identity remains subject to exact validation. This optional declarative policy uses the existing cumulative runtime; runtime/core/Builder/tester implementations are unchanged. Original descriptor sequence values remain provenance. Frozen campaigns are not modified. This source inspection does not establish deployed-pod binary hash equality or itself grant live import authority.

## Captured source hashes
The private research checkpoint retains capture locations. Shipping references contain portable class/JAR identities and exact evidence hashes only.

{
  "seedScopedSha256": "70ae55ad0ca201cc04d240d112c7846f2be49e7715719cd19e0c574e86ef5a31",
  "frameworkEvidence": [
    {
      "className": "oracle/apps/setup/migrator/configurationPackages/model/applicationModule/ConfigurationPackageAMHelper.class",
      "jar": "AdfSetupModel.jar",
      "jarSha256": "e23a87f99c0b4660d9392272b0c3b71978ad60bffbd4583b3dc683f8ce537e5d",
      "exitCode": 0,
      "diagnostic": "",
      "textSha256": "e9e41b33a299c60298350a8783b961cfaff56a75edcef7dc47df91d3755a53ca"
    },
    {
      "className": "oracle/apps/setupHub/xml/model/applicationModule/XmlCSVAMImpl.class",
      "jar": "AdfFunctionalSetupPublicModel.jar",
      "jarSha256": "05dd79fe2c7b6fdb3ae0f518d15e57adb85261069870743d36fd474b0feeded6",
      "exitCode": 0,
      "diagnostic": "",
      "textSha256": "55e84a21549a937558764ef78eec9d23b892ff7f5e1676a7608be6c22ee4b25c"
    }
  ]
}
