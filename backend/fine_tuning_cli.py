#!/usr/bin/env python3
"""
Phase 5C Training CLI

Command-line interface for fine-tuning MedSAM models on custom medical datasets.

Usage:
    python fine_tuning_cli.py --dataset-dir ./data/images --mask-dir ./data/masks --epochs 10
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional
import torch
from torch.utils.data import DataLoader
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fine-tune MedSAM on custom medical datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train on custom dataset
  python fine_tuning_cli.py \\
    --dataset-dir ./data/images \\
    --mask-dir ./data/masks \\
    --epochs 10 \\
    --batch-size 4 \\
    --learning-rate 1e-4
  
  # Resume training from checkpoint
  python fine_tuning_cli.py \\
    --dataset-dir ./data/images \\
    --mask-dir ./data/masks \\
    --checkpoint ./checkpoints/latest.pt \\
    --epochs 20
  
  # Validate model on test set
  python fine_tuning_cli.py \\
    --dataset-dir ./data/test \\
    --mask-dir ./data/test_masks \\
    --checkpoint ./checkpoints/best.pt \\
    --validate-only
        """
    )
    
    # Dataset arguments
    parser.add_argument(
        '--dataset-dir',
        type=str,
        required=True,
        help='Directory containing training images'
    )
    parser.add_argument(
        '--mask-dir',
        type=str,
        required=False,
        help='Directory containing segmentation masks'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./checkpoints',
        help='Output directory for checkpoints (default: ./checkpoints)'
    )
    
    # Training arguments
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        help='Number of training epochs (default: 10)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=4,
        help='Batch size (default: 4)'
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=1e-4,
        help='Learning rate (default: 1e-4)'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='cpu',
        choices=['cpu', 'cuda'],
        help='Device to train on (default: cpu)'
    )
    
    # Checkpoint arguments
    parser.add_argument(
        '--checkpoint',
        type=str,
        help='Path to checkpoint to resume training or validate'
    )
    
    # Validation/testing
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only run validation, do not train'
    )
    parser.add_argument(
        '--test-images-dir',
        type=str,
        help='Directory for test/validation images (if different from training)'
    )
    
    # Logging
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate inputs
    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.exists():
        logger.error(f"Dataset directory not found: {dataset_dir}")
        sys.exit(1)
    
    mask_dir = Path(args.mask_dir) if args.mask_dir else None
    if mask_dir and not mask_dir.exists():
        logger.error(f"Mask directory not found: {mask_dir}")
        sys.exit(1)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check device
    device = args.device
    if device == 'cuda' and not torch.cuda.is_available():
        logger.warning("CUDA not available, falling back to CPU")
        device = 'cpu'
    
    logger.info(f"✓ Device: {device}")
    
    # Import models
    try:
        from app.services.phase_5_services.medsam_fine_tuner import (
            get_medsam_fine_tuner,
            MedicalImageDataset
        )
        from app.services.phase_5_api_handler import get_phase_5_handler
    except ImportError as e:
        logger.error(f"Failed to import training modules: {e}")
        sys.exit(1)
    
    try:
        # Get Phase 5 handler (includes MedSAM model)
        handler = get_phase_5_handler()
        
        if not handler:
            logger.error("Failed to initialize Phase 5 handler")
            sys.exit(1)
        
        # Check if model is loaded
        if not handler.current_model:
            logger.error("MedSAM model not loaded in Phase 5 handler")
            sys.exit(1)
        
        logger.info(f"✓ MedSAM model loaded: {handler.current_model_name}")
        
        # Create dataset
        logger.info(f"Loading dataset from {dataset_dir}...")
        dataset = MedicalImageDataset(
            image_dir=str(dataset_dir),
            mask_dir=str(mask_dir) if mask_dir else None,
            image_size=(1024, 1024),
            augmentation=not args.validate_only
        )
        
        logger.info(f"✓ Dataset loaded: {len(dataset)} images")
        
        # Create data loader
        data_loader = DataLoader(
            dataset,
            batch_size=args.batch_size,
            shuffle=not args.validate_only,
            num_workers=0
        )
        
        logger.info(f"✓ DataLoader created: {len(data_loader)} batches")
        
        # Initialize fine-tuner
        fine_tuner = get_medsam_fine_tuner(handler.current_model, device)
        
        if args.validate_only:
            # Validation only
            logger.info("Running validation...")
            metrics = fine_tuner._validate_epoch(data_loader)
            
            logger.info("\n=== Validation Results ===")
            logger.info(f"Loss: {metrics.get('loss', 'N/A'):.4f}")
            logger.info(f"Dice Score: {metrics.get('dice', 'N/A'):.4f}")
            logger.info(f"IoU: {metrics.get('iou', 'N/A'):.4f}")
            
            # Save results
            results_file = output_dir / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"✓ Results saved to {results_file}")
        else:
            # Training
            logger.info(f"Starting training for {args.epochs} epochs...")
            logger.info(f"Learning rate: {args.learning_rate}")
            logger.info(f"Batch size: {args.batch_size}")
            
            # Resume from checkpoint if provided
            if args.checkpoint:
                logger.info(f"Resuming from checkpoint: {args.checkpoint}")
                fine_tuner.load_checkpoint(args.checkpoint)
            
            # Train
            result = fine_tuner.train(
                train_loader=data_loader,
                val_loader=data_loader,  # Use same loader for now
                num_epochs=args.epochs,
                learning_rate=args.learning_rate
            )
            
            # Print results
            logger.info("\n=== Training Complete ===")
            logger.info(f"Epochs trained: {result.get('epochs', 0)}")
            logger.info(f"Best loss: {result.get('best_loss', 'N/A'):.4f}")
            logger.info(f"Checkpoint dir: {result.get('checkpoint_dir')}")
            
            # Save training history
            history_file = output_dir / f"training_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            history_data = {
                "config": {
                    "epochs": args.epochs,
                    "batch_size": args.batch_size,
                    "learning_rate": args.learning_rate,
                    "device": device,
                    "dataset_size": len(dataset)
                },
                "results": result,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            logger.info(f"✓ Training history saved to {history_file}")
        
        logger.info("✓ Done!")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("\n[INTERRUPTED] Training stopped by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
