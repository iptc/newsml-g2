#!/bin/bash

XSD_PATH="specification/individual"
OLD_VERSION="2.28"
NEW_VERSION="2.28_2"

git mv $XSD_PATH/NewsML-G2_$OLD_VERSION-spec-CatalogItem-Power.xsd $XSD_PATH/NewsML-G2_$NEW_VERSION-spec-CatalogItem-Power.xsd
git mv $XSD_PATH/NewsML-G2_$OLD_VERSION-spec-PackageItem-Power.xsd $XSD_PATH/NewsML-G2_$NEW_VERSION-spec-PackageItem-Power.xsd
git mv $XSD_PATH/NewsML-G2_$OLD_VERSION-spec-ConceptItem-Power.xsd $XSD_PATH/NewsML-G2_$NEW_VERSION-spec-ConceptItem-Power.xsd
git mv $XSD_PATH/NewsML-G2_$OLD_VERSION-spec-PlanningItem-Power.xsd $XSD_PATH/NewsML-G2_$NEW_VERSION-spec-PlanningItem-Power.xsd
git mv $XSD_PATH/NewsML-G2_$OLD_VERSION-spec-KnowledgeItem-Power.xsd $XSD_PATH/NewsML-G2_$NEW_VERSION-spec-KnowledgeItem-Power.xsd
git mv $XSD_PATH/NewsML-G2_$OLD_VERSION-spec-NewsItem-Power.xsd $XSD_PATH/NewsML-G2_$NEW_VERSION-spec-NewsItem-Power.xsd
git mv $XSD_PATH/NewsML-G2_$OLD_VERSION-spec-Framework-Power.xsd $XSD_PATH/NewsML-G2_$NEW_VERSION-spec-Framework-Power.xsd
git mv $XSD_PATH/NewsML-G2_$OLD_VERSION-spec-NewsMessage-Power.xsd $XSD_PATH/NewsML-G2_$NEW_VERSION-spec-NewsMessage-Power.xsd
