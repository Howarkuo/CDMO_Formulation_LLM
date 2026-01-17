class PublisherMap:
    # Comprehensive DOI prefixes
    PREFIXES = {
        # Elsevier (ScienceDirect, Cell, The Lancet)
        "10.1016": "Elsevier",
        
        # Springer Nature Group
        "10.1007": "Springer",
        "10.1038": "Nature",
        "10.1186": "BMC",
        
        # Wiley (Advanced Materials, Angewandte Chemie)
        "10.1002": "Wiley",
        "10.1111": "Wiley",
        
        # Taylor & Francis (Routledge, CRC)
        "10.1080": "TaylorFrancis",
        
        # American Chemical Society (JACS, Chem Reviews)
        "10.1021": "ACS",
        
        # IEEE (Transactions, Xplore)
        "10.1109": "IEEE",
        
        # AAAS (Science)
        "10.1126": "Science",
        
        # MDPI (Molecules, Sensors)
        "10.3390": "MDPI",
        
        # PLOS (Public Library of Science)
        "10.1371": "PLOS",
        
        # Frontiers
        "10.3389": "Frontiers",
        
        # Oxford University Press
        "10.1093": "Oxford",
        
        # Cambridge University Press
        "10.1017": "Cambridge",
        
        # SAGE Publishing
        "10.1177": "SAGE",
        
        # Royal Society of Chemistry
        "10.1039": "RSC",
        
        # Physics (AIP, APS)
        "10.1063": "AIP",
        "10.1103": "APS"
    }

    @staticmethod
    def identify_publisher(doi):
        """
        Returns the publisher name based on the DOI prefix.
        Example: '10.1016/j.ijpharm.2023.x' -> 'Elsevier'
        """
        if not doi:
            return "Unknown"
            
        # Extract the prefix (part before the first slash)
        try:
            prefix = doi.split('/')[0]
            return PublisherMap.PREFIXES.get(prefix, "Other")
        except IndexError:
            return "Invalid DOI"

    @staticmethod
    def is_elsevier(doi):
        """Helper to quickly check if a DOI belongs to Elsevier."""
        return PublisherMap.identify_publisher(doi) == "Elsevier"